"""AcademicYear model."""
from django.core.exceptions import ValidationError
from django.db import models

from domain.academic.constants import AcademicYearStatus
from domain.shared.models.base import AuditModel
from domain.shared.models.managers import BaseManager


class AcademicYearManager(BaseManager):
    """Custom manager for AcademicYear model."""

    def get_current(self):
        """Get the current academic year."""
        return self.filter(is_current=True).first()

    def get_active(self):
        """Get all active academic years."""
        return self.filter(status=AcademicYearStatus.ACTIVE)


class AcademicYear(AuditModel):
    """
    Represents a global academic year reference.

    Business Rules:
        - Only one academic year can have is_current = True
        - end_year must equal start_year + 1
        - Code format: "YYYY-YYYY" (e.g., "2024-2025")
        - Cannot be physically deleted
        - ARCHIVED years cannot be modified or set as current
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        help_text="Code court (ex. 2024-2025) - Auto-generated if not provided",
    )
    start_year = models.IntegerField(help_text="Année de début (ex. 2024)")
    end_year = models.IntegerField(help_text="Année de fin (ex. 2025)")
    is_current = models.BooleanField(
        default=False,
        help_text="Année académique en cours",
    )
    status = models.CharField(
        max_length=20,
        choices=AcademicYearStatus.CHOICES,
        default=AcademicYearStatus.DRAFT,
        help_text="Statut de l'année académique",
        db_index=True,
    )

    # Custom manager
    objects = AcademicYearManager()

    class Meta:
        db_table = "academic_year"
        verbose_name = "Academic Year"
        verbose_name_plural = "Academic Years"
        ordering = ["-start_year"]
        indexes = [
            models.Index(fields=["is_current"], name="academic_year_is_current_idx"),
            models.Index(fields=["status"], name="academic_year_status_idx"),
            models.Index(fields=["start_year"], name="academic_year_start_year_idx"),
            models.Index(fields=["start_year", "end_year"], name="academic_year_period_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["start_year", "end_year"],
                condition=models.Q(is_deleted=False),
                name="unique_academic_year_period",
            ),
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_academic_year_code",
            ),
        ]

    def __str__(self):
        return self.code

    def clean(self):
        """Validate model fields."""
        super().clean()

        # Validate year sequence
        if self.end_year != self.start_year + 1:
            raise ValidationError(
                {"end_year": "End year must be start_year + 1"}
            )

        # Auto-generate code if not provided
        if not self.code:
            self.code = f"{self.start_year}-{self.end_year}"

        # Validate code format
        expected_code = f"{self.start_year}-{self.end_year}"
        if self.code != expected_code:
            raise ValidationError(
                {"code": f"Code must be '{expected_code}'"}
            )

        # Only one current year allowed
        if self.is_current:
            existing_current = (
                AcademicYear.active.filter(is_current=True)
                .exclude(pk=self.pk)
                .exists()
            )
            if existing_current:
                raise ValidationError(
                    {"is_current": "Only one academic year can be current"}
                )

        # ARCHIVED years cannot be current
        if self.status == AcademicYearStatus.ARCHIVED and self.is_current:
            raise ValidationError(
                {"is_current": "Archived years cannot be set as current"}
            )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        # If setting as current, unset others BEFORE validation
        if self.is_current:
            AcademicYear.active.filter(is_current=True).exclude(
                pk=self.pk
            ).update(is_current=False)
        
        self.full_clean()
        super().save(*args, **kwargs)

    def archive(self):
        """Archive this academic year."""
        if self.status == AcademicYearStatus.ARCHIVED:
            return

        self.status = AcademicYearStatus.ARCHIVED
        self.is_current = False
        self.save(update_fields=["status", "is_current", "updated_at"])

    def activate(self):
        """Activate this academic year."""
        if self.status == AcademicYearStatus.ARCHIVED:
            raise ValidationError("Cannot activate an archived year")

        self.status = AcademicYearStatus.ACTIVE
        self.save(update_fields=["status", "updated_at"])
