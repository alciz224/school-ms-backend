"""StudentEnrollment model (Enrollment domain)."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.account.models import CustomUser
from domain.enrollment.models.classroom import Classroom
from domain.enrollment.models.constants import StudentEnrollmentStatus
from domain.school_operations.models import SchoolYearLevel
from domain.shared.models.base import AuditModel


class StudentEnrollment(AuditModel):
    """
    Enrollment of a student for a given SchoolYearLevel, optionally assigned to a Classroom.

    Note on identifiers (per project decision):
    - We only keep `annual_identifier` and `classroom_identifier`.
    - No level_identifier / same-name identifiers in this version.

    Core rules:
    - Unique per (student, school_year_level) for non-deleted records.
    - classroom can be null for PRE_REGISTERED.
    - Date coherence: start_date >= enrollment_date; end_date >= start_date.
    """

    # Optional: some students do not have a platform account.
    student = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
        null=True,
        blank=True,
    )
    # Snapshot identity for non-account students and for historical consistency.
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)

    school_year_level = models.ForeignKey(
        SchoolYearLevel,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="student_enrollments",
        null=True,
        blank=True,
    )
    previous_classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="student_enrollments_previous",
        null=True,
        blank=True,
    )

    enrollment_status = models.CharField(
        max_length=20,
        choices=StudentEnrollmentStatus.choices,
        default=StudentEnrollmentStatus.PRE_REGISTERED,
    )

    enrollment_date = models.DateField()
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    transfer_reason = models.CharField(max_length=255, null=True, blank=True)

    annual_identifier = models.CharField(max_length=64)
    classroom_identifier = models.CharField(max_length=64, null=True, blank=True)

    # Optional suffix used to disambiguate same-name students within the same classroom.
    # Rule (A): suffix is NULL when no collision; when a collision occurs, the first becomes 1 and the next 2, etc.
    classroom_suffix = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        db_table = "student_enrollment"
        verbose_name = "Student Enrollment"
        verbose_name_plural = "Student Enrollments"
        ordering = ["-enrollment_date", "last_name", "first_name"]
        indexes = [
            models.Index(fields=["student", "school_year_level"], name="enroll_student_syl_idx"),
            models.Index(fields=["school_year_level", "classroom"], name="enroll_syl_class_idx"),
            models.Index(fields=["annual_identifier"], name="enroll_annual_ident_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "first_name", "last_name", "classroom_suffix"],
                condition=models.Q(is_deleted=False, classroom__isnull=False, classroom_suffix__isnull=False),
                name="unique_classroom_name_suffix",
            ),
            # Only enforce uniqueness when student account exists.
            models.UniqueConstraint(
                fields=["student", "school_year_level"],
                condition=models.Q(is_deleted=False, student__isnull=False),
                name="unique_student_enrollment_per_level",
            ),
            models.UniqueConstraint(
                fields=["annual_identifier"],
                condition=models.Q(is_deleted=False),
                name="unique_student_enrollment_annual_identifier",
            ),
        ]

    def __str__(self) -> str:
        ident = self.annual_identifier
        return f"{self.display_name} ({ident})"

    @property
    def display_name(self) -> str:
        if self.classroom_suffix is None:
            return f"{self.first_name} {self.last_name}".strip()
        return f"{self.first_name} {self.classroom_suffix} {self.last_name}".strip()

    def clean(self):
        super().clean()

        # Student name snapshot should be present
        if not self.first_name:
            raise ValidationError({"first_name": "First name is required."})
        if not self.last_name:
            raise ValidationError({"last_name": "Last name is required."})

        # Pre-registered may have no classroom; others should.
        if self.enrollment_status != StudentEnrollmentStatus.PRE_REGISTERED and not self.classroom_id:
            raise ValidationError({"classroom": "Classroom is required when enrollment is not pre-registered."})

        # Suffix is only allowed/meaningful when classroom is present
        if not self.classroom_id and self.classroom_suffix is not None:
            raise ValidationError({"classroom_suffix": "Suffix requires a classroom."})

        # classroom must belong to same school_year_level
        if self.classroom_id and self.school_year_level_id:
            if self.classroom.school_year_level_id != self.school_year_level_id:
                raise ValidationError({"classroom": "Classroom must belong to the same SchoolYearLevel."})

        if self.previous_classroom_id and self.school_year_level_id:
            if self.previous_classroom.school_year_level_id != self.school_year_level_id:
                raise ValidationError({"previous_classroom": "Previous classroom must belong to the same SchoolYearLevel."})

        # dates coherence
        if self.start_date and self.enrollment_date and self.start_date < self.enrollment_date:
            raise ValidationError({"start_date": "Start date must be >= enrollment date."})
        if self.end_date and self.start_date and self.end_date < self.start_date:
            raise ValidationError({"end_date": "End date must be >= start date."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
