"""ReportCardSubject model."""

from django.db import models

from domain.assessment.models.report_card import ReportCard
from domain.school_operations.models import SchoolYearLevelSubject
from domain.shared.models.base import AuditModel


class ReportCardSubject(AuditModel):
    """
    Subject line in a report card (per subject).

    Business Rules:
        - Unique per (report_card, school_year_level_subject)
        - Average should be computed from VALIDATED grades only
    """

    report_card = models.ForeignKey(
        ReportCard,
        on_delete=models.PROTECT,
        related_name="subjects",
        help_text="Parent report card",
    )
    school_year_level_subject = models.ForeignKey(
        SchoolYearLevelSubject,
        on_delete=models.PROTECT,
        related_name="report_card_subjects",
        help_text="Subject + coefficient",
    )

    average = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average score for this subject",
    )
    coefficient = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text="Coefficient used for weighting",
    )
    teacher_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional teacher name snapshot",
    )
    remark = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional subject remark",
    )

    class Meta:
        db_table = "report_card_subject"
        verbose_name = "Report Card Subject"
        verbose_name_plural = "Report Card Subjects"
        ordering = ["report_card", "school_year_level_subject"]
        constraints = [
            models.UniqueConstraint(
                fields=["report_card", "school_year_level_subject"],
                condition=models.Q(is_deleted=False),
                name="unique_report_card_subject",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.report_card} - {self.school_year_level_subject.subject.name}"
