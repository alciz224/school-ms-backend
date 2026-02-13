"""Transcript model (annual report)."""

from django.db import models

from domain.enrollment.models import StudentEnrollment
from domain.school_operations.models import SchoolYear
from domain.shared.models.base import AuditModel


class Transcript(AuditModel):
    """
    Annual transcript for a student, aggregated from ReportCards.

    Business Rules:
        - Unique per (student_enrollment, school_year)
        - Derived from finalized report cards
        - Decision is manual (optional)
    """

    student_enrollment = models.ForeignKey(
        StudentEnrollment,
        on_delete=models.PROTECT,
        related_name="transcripts",
        help_text="Student enrollment",
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="transcripts",
        help_text="School year",
    )

    overall_average = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Annual weighted average",
    )
    decision = models.CharField(
        max_length=50,
        blank=True,
        help_text="Manual decision (PASS/FAIL/REPEAT, etc.)",
    )

    generated_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when transcript was generated",
    )

    raw_data = models.JSONField(
        default=dict,
        blank=True,
        help_text="Snapshot of aggregated data for audit/export",
    )

    class Meta:
        db_table = "transcript"
        verbose_name = "Transcript"
        verbose_name_plural = "Transcripts"
        ordering = ["school_year", "student_enrollment"]
        constraints = [
            models.UniqueConstraint(
                fields=["student_enrollment", "school_year"],
                condition=models.Q(is_deleted=False),
                name="unique_transcript_per_student_year",
            ),
        ]

    def __str__(self) -> str:
        return f"Transcript({self.student_enrollment} - {self.school_year})"
