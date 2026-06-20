"""SchoolYearCycle model."""
from django.core.exceptions import ValidationError
from django.db import models

from domain.academic.models import Cycle, TermType
from domain.school_operations.models.school_year import SchoolYear
from domain.shared.models.base import AuditModel


class SchoolYearCycle(AuditModel):
    """
    Represents a cycle taught in a school for a specific school year.

    Links a master Cycle to a SchoolYear and defines the TermType used
    for that cycle in that year. Serves as a container for levels and assessments.

    Business Rules:
        - Each (school_year, cycle) combination must be unique
        - term_type must be consistent with the school_year duration
        - Cannot be deleted if levels or assessments are associated
        - Immutable once levels or assessments are created

    Examples:
        - School Year 2024-2025, Cycle "Primaire", TermType "Trimester"
        - School Year 2024-2025, Cycle "Lycée", TermType "Semester"
    """

    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="cycles",
        help_text="Année scolaire associée",
    )
    cycle = models.ForeignKey(
        Cycle,
        on_delete=models.PROTECT,
        related_name="school_year_cycles",
        help_text="Cycle enseigné (référence master)",
    )
    term_type = models.ForeignKey(
        TermType,
        on_delete=models.PROTECT,
        related_name="school_year_cycles",
        help_text="Type de période pour ce cycle (trimestre, semestre, etc.)",
    )

    class Meta:
        db_table = "school_year_cycle"
        verbose_name = "School Year Cycle"
        verbose_name_plural = "School Year Cycles"
        ordering = ["school_year", "cycle"]
        indexes = [
            models.Index(
                fields=["school_year", "cycle"],
                name="syc_school_year_cycle_idx",
            ),
            models.Index(
                fields=["school_year", "term_type"],
                name="syc_school_year_term_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "cycle"],
                condition=models.Q(is_deleted=False),
                name="unique_school_year_cycle",
            ),
        ]

    def __str__(self):
        return f"{self.school_year} - {self.cycle} ({self.term_type})"

    def clean(self):
        """Validate model fields and business rules."""
        super().clean()

        # Additional business logic validation can be added here
        # For example, validating that school_year is not in the past
        # or that term_type is compatible with school_year duration
        pass

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def can_delete(self):
        """
        Check if the cycle can be deleted.

        A cycle cannot be removed while non-deleted levels are still attached
        to it (those levels must be removed first).

        Returns:
            bool: True if can be deleted, False otherwise
        """
        if self.levels.filter(is_deleted=False).exists():
            return False

        return True

    def get_levels(self):
        """
        Get all levels associated with this cycle.

        Returns:
            QuerySet: SchoolYearLevel queryset (when implemented)
        """
        # Placeholder for when SchoolYearLevel is implemented
        # return self.levels.filter(is_deleted=False)
        return None
