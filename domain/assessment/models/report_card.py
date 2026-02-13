"""ReportCard model (Assessment reporting)."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.enrollment.models import StudentEnrollment
from domain.school_operations.models import SchoolYearCycleTerm
from domain.shared.models.base import AuditModel


class ReportCard(AuditModel):
    """
    Persisted report card for a student in a given term.

    Business Rules:
        - Unique per (student_enrollment, school_year_cycle_term)
        - Report cards are frozen when is_final=True
        - Only VALIDATED grades are used in generation
        - Absences are excluded from averages
        - Overall average is weighted by subject coefficient
        - Rank is computed per classroom + term
    """

    student_enrollment = models.ForeignKey(
        StudentEnrollment,
        on_delete=models.PROTECT,
        related_name="report_cards",
        help_text="Student enrollment for this report card",
    )
    school_year_cycle_term = models.ForeignKey(
        SchoolYearCycleTerm,
        on_delete=models.PROTECT,
        related_name="report_cards",
        help_text="Term for this report card",
    )
    classroom = models.ForeignKey(
        "enrollment.Classroom",
        on_delete=models.PROTECT,
        related_name="report_cards",
        help_text="Classroom where the student is enrolled",
    )

    overall_average = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Weighted overall average for this term",
    )
    rank = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Class rank for this term (per classroom)",
    )
    decision = models.CharField(
        max_length=50,
        blank=True,
        help_text="Manual decision (optional)",
    )

    generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when report card was generated",
    )
    is_final = models.BooleanField(
        default=False,
        help_text="Frozen report card; cannot be modified when True",
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of computed data for audit and export",
    )

    class Meta:
        db_table = "report_card"
        verbose_name = "Report Card"
        verbose_name_plural = "Report Cards"
        ordering = ["school_year_cycle_term", "classroom", "student_enrollment"]
        indexes = [
            models.Index(fields=["school_year_cycle_term", "classroom"], name="report_card_term_class_idx"),
            models.Index(fields=["student_enrollment"], name="report_card_student_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["student_enrollment", "school_year_cycle_term"],
                condition=models.Q(is_deleted=False),
                name="unique_report_card_per_student_term",
            ),
        ]

    def __str__(self) -> str:
        return f"ReportCard({self.student_enrollment} - {self.school_year_cycle_term})"

    def clean(self):
        super().clean()

        # Ensure classroom consistency
        if self.student_enrollment_id and self.classroom_id:
            if self.student_enrollment.classroom_id != self.classroom_id:
                raise ValidationError({
                    "classroom": "Classroom must match student's enrollment classroom."
                })

        # Ensure term consistency with enrollment's school year
        if self.student_enrollment_id and self.school_year_cycle_term_id:
            sy_id = self.student_enrollment.school_year_level.school_year_cycle.school_year_id
            if self.school_year_cycle_term.school_year_cycle.school_year_id != sy_id:
                raise ValidationError({
                    "school_year_cycle_term": "Term must belong to the same school year as the enrollment."
                })

    def save(self, *args, **kwargs):
        if self.pk and self.is_final:
            raise ValidationError("Final report cards cannot be modified.")
        self.full_clean()
        return super().save(*args, **kwargs)
