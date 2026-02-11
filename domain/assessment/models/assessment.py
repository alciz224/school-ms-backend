"""Assessment model (Assessment domain)."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.academic.models import AssessmentType
from domain.assessment.constants import AssessmentStatus, ASSESSMENT_STATUS_TRANSITIONS
from domain.school_operations.models import SchoolYear, SchoolYearCycle, SchoolYearCycleTerm
from domain.shared.models.base import AuditModel


class Assessment(AuditModel):
    """
    Assessment framework for a specific period/cycle (e.g., "Trimester 1 Exams").
    
    Represents the global evaluation context that groups multiple AssessmentSubject.
    
    Business Rules:
        - Unique per (school_year_cycle, assessment_type, school_year_cycle_term)
        - Only one assessment per type/period/cycle
        - start_date <= end_date
        - Dates must fall within school_year_cycle_term period
        - Status workflow: DRAFT → ACTIVE → CLOSED → ARCHIVED
        - AssessmentSubject can only be created when status is ACTIVE
    """

    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="assessments",
        help_text="School year for this assessment",
    )
    school_year_cycle = models.ForeignKey(
        SchoolYearCycle,
        on_delete=models.PROTECT,
        related_name="assessments",
        help_text="Specific cycle for this assessment",
    )
    school_year_cycle_term = models.ForeignKey(
        SchoolYearCycleTerm,
        on_delete=models.PROTECT,
        related_name="assessments",
        help_text="Specific term period for this assessment",
    )
    assessment_type = models.ForeignKey(
        AssessmentType,
        on_delete=models.PROTECT,
        related_name="assessments",
        help_text="Type of assessment (exam, test, project, etc.)",
    )
    
    name = models.CharField(
        max_length=200,
        help_text="Name of the assessment (e.g., 'Trimester 1 Exams')",
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of the assessment",
    )
    
    status = models.CharField(
        max_length=20,
        choices=AssessmentStatus.choices,
        default=AssessmentStatus.DRAFT,
        help_text="Status of the assessment",
    )
    
    start_date = models.DateField(
        help_text="Start date for the assessment period",
    )
    end_date = models.DateField(
        help_text="End date for the assessment period",
    )

    class Meta:
        db_table = "assessment"
        verbose_name = "Assessment"
        verbose_name_plural = "Assessments"
        ordering = ["-start_date", "assessment_type"]
        indexes = [
            models.Index(fields=["school_year_cycle", "assessment_type"], name="assess_cycle_type_idx"),
            models.Index(fields=["status"], name="assess_status_idx"),
            models.Index(fields=["start_date", "end_date"], name="assess_dates_idx"),
        ]
        constraints = [
            # Unique assessment per type/period/cycle
            models.UniqueConstraint(
                fields=["school_year_cycle", "assessment_type", "school_year_cycle_term"],
                condition=models.Q(is_deleted=False),
                name="unique_assessment_per_type_period_cycle",
            ),
            # Date coherence
            models.CheckConstraint(
                condition=models.Q(start_date__lte=models.F("end_date")),
                name="assessment_dates_coherent",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.school_year_cycle}) [{self.status}]"

    def clean(self):
        super().clean()

        # Date coherence
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        # Coherence: school_year_cycle_term must belong to school_year_cycle
        if self.school_year_cycle_id and self.school_year_cycle_term_id:
            if self.school_year_cycle_term.school_year_cycle_id != self.school_year_cycle_id:
                raise ValidationError({
                    "school_year_cycle_term": "Term must belong to the same school year cycle."
                })

        # Coherence: school_year_cycle must belong to school_year  
        if self.school_year_id and self.school_year_cycle_id:
            if self.school_year_cycle.school_year_id != self.school_year_id:
                raise ValidationError({
                    "school_year_cycle": "Cycle must belong to the same school year."
                })

        # Dates must fall within school_year_cycle_term period
        if self.school_year_cycle_term_id and self.start_date and self.end_date:
            term = self.school_year_cycle_term
            if self.start_date < term.start_date or self.end_date > term.end_date:
                raise ValidationError({
                    "start_date": f"Assessment dates must fall within term period ({term.start_date} - {term.end_date})."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition to new status is allowed."""
        allowed_transitions = ASSESSMENT_STATUS_TRANSITIONS.get(self.status, [])
        return new_status in allowed_transitions

    @property
    def is_active(self) -> bool:
        """Check if assessment is currently active."""
        return self.status == AssessmentStatus.ACTIVE and not self.is_deleted

    @property
    def can_create_subjects(self) -> bool:
        """Check if new AssessmentSubject can be created."""
        return self.is_active

    @property
    def is_closed_or_archived(self) -> bool:
        """Check if assessment is closed or archived."""
        return self.status in [AssessmentStatus.CLOSED, AssessmentStatus.ARCHIVED]