"""SchoolYearCycleTerm model."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.academic.models import Term
from domain.school_operations.models.school_year_cycle import SchoolYearCycle
from domain.shared.models.base import AuditModel


class SchoolYearCycleTerm(AuditModel):
    """
    Links a concrete Term to a SchoolYearCycle with specific dates.
    
    Represents an actual academic period (e.g., Trimester 1 from Sept 1 to Dec 15)
    for a specific cycle in a school year.
    
    Business Rules:
        - Unique per (school_year_cycle, term) for non-deleted records
        - start_date < end_date
        - Dates must fall within the school_year_cycle's school_year dates
        - Term must belong to the same TermType as school_year_cycle.term_type
        - Cannot overlap with other terms in the same cycle
    """

    school_year_cycle = models.ForeignKey(
        SchoolYearCycle,
        on_delete=models.PROTECT,
        related_name="cycle_terms",
        help_text="School year cycle for this term period",
    )
    term = models.ForeignKey(
        Term,
        on_delete=models.PROTECT,
        related_name="year_cycle_assignments",
        help_text="Master term reference (e.g., T1, T2, S1)",
    )
    start_date = models.DateField(
        help_text="Start date for this period",
    )
    end_date = models.DateField(
        help_text="End date for this period",
    )

    class Meta:
        db_table = "school_year_cycle_term"
        verbose_name = "School Year Cycle Term"
        verbose_name_plural = "School Year Cycle Terms"
        ordering = ["school_year_cycle", "term__order"]
        indexes = [
            models.Index(fields=["school_year_cycle", "term"], name="syc_term_idx"),
            models.Index(fields=["start_date", "end_date"], name="syc_term_dates_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year_cycle", "term"],
                condition=models.Q(is_deleted=False),
                name="unique_school_year_cycle_term",
            ),
            models.CheckConstraint(
                condition=models.Q(start_date__lt=models.F("end_date")),
                name="school_year_cycle_term_dates_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.school_year_cycle} - {self.term}"

    def clean(self):
        super().clean()

        # Dates coherence
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        # Term must belong to cycle's term_type
        if self.term_id and self.school_year_cycle_id:
            if self.term.term_type_id != self.school_year_cycle.term_type_id:
                raise ValidationError({
                    "term": f"Term must belong to term type '{self.school_year_cycle.term_type}'."
                })

        # Dates must fall within school year
        if self.school_year_cycle_id and self.start_date and self.end_date:
            school_year = self.school_year_cycle.school_year
            if self.start_date < school_year.start_date or self.end_date > school_year.end_date:
                raise ValidationError({
                    "start_date": "Term dates must fall within the school year period.",
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
