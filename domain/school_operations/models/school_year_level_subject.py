"""SchoolYearLevelSubject model."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.academic.models import Subject
from domain.school_operations.models.school_year_level import SchoolYearLevel
from domain.shared.models.base import AuditModel


class SchoolYearLevelSubject(AuditModel):
    """
    Links a Subject to a SchoolYearLevel with a specific coefficient.
    
    This represents the concrete assignment of a subject to a level for a specific school year,
    with the weighting (coefficient) used for grade calculations.
    
    Business Rules:
        - Unique per (school_year_level, subject) for non-deleted records
        - Coefficient must be > 0
        - Cannot be deleted if assessments/grades exist
    """

    school_year_level = models.ForeignKey(
        SchoolYearLevel,
        on_delete=models.PROTECT,
        related_name="level_subjects",
        help_text="School year level for this subject assignment",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="year_level_assignments",
        help_text="Master subject reference",
    )
    coefficient = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Weight/coefficient for grade calculation (must be > 0)",
    )

    class Meta:
        db_table = "school_year_level_subject"
        verbose_name = "School Year Level Subject"
        verbose_name_plural = "School Year Level Subjects"
        ordering = ["school_year_level", "subject"]
        indexes = [
            models.Index(fields=["school_year_level", "subject"], name="syl_subject_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year_level", "subject"],
                condition=models.Q(is_deleted=False),
                name="unique_school_year_level_subject",
            ),
            models.CheckConstraint(
                condition=models.Q(coefficient__gt=0),
                name="school_year_level_subject_coefficient_positive",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.school_year_level} - {self.subject} (coef: {self.coefficient})"

    def clean(self):
        super().clean()
        if self.coefficient is not None and self.coefficient <= 0:
            raise ValidationError({"coefficient": "Coefficient must be greater than 0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
