"""SchoolYearTeacher model."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.account.models import CustomUser
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models.school_year import SchoolYear
from domain.shared.models.base import AuditModel


class SchoolYearTeacher(AuditModel):
    """
    Represents a teacher assigned to a school for a specific school year.
    
    Acts as a prerequisite for TeacherAssignment (classroom/subject assignments).
    Controls which teachers can teach during a school year.
    
    Business Rules:
        - Unique per (school_year, teacher) for non-deleted records
        - SUSPENDED or LEFT teachers cannot receive new assignments
        - Existing assignments remain intact for history
        - hire_date and end_date optional but must be coherent if provided
    """

    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="year_teachers",
        help_text="School year for this teacher assignment",
    )
    teacher = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="school_year_assignments",
        help_text="Teacher user (must have teacher role in session)",
    )
    status = models.CharField(
        max_length=20,
        choices=SchoolYearTeacherStatus.choices,
        default=SchoolYearTeacherStatus.ACTIVE,
        help_text="Status of the teacher for this school year",
    )
    hire_date = models.DateField(
        null=True,
        blank=True,
        help_text="Start date of activity for this school year",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date of activity (if teacher left)",
    )

    class Meta:
        db_table = "school_year_teacher"
        verbose_name = "School Year Teacher"
        verbose_name_plural = "School Year Teachers"
        ordering = ["school_year", "teacher"]
        indexes = [
            models.Index(fields=["school_year", "teacher"], name="sy_teacher_idx"),
            models.Index(fields=["status"], name="sy_teacher_status_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "teacher"],
                condition=models.Q(is_deleted=False),
                name="unique_school_year_teacher",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.teacher} - {self.school_year} ({self.status})"

    def clean(self):
        super().clean()

        # Date coherence
        if self.hire_date and self.end_date and self.hire_date >= self.end_date:
            raise ValidationError({"end_date": "End date must be after hire date."})

        # Dates must fall within school year
        if self.school_year_id:
            if self.hire_date and self.hire_date < self.school_year.start_date:
                raise ValidationError({"hire_date": "Hire date must be within the school year period."})
            if self.end_date and self.end_date > self.school_year.end_date:
                raise ValidationError({"end_date": "End date must be within the school year period."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def can_receive_assignments(self) -> bool:
        """Check if teacher can receive new classroom/subject assignments."""
        return self.status == SchoolYearTeacherStatus.ACTIVE and not self.is_deleted
