"""Term model."""
from django.core.exceptions import ValidationError
from django.db import models

from domain.shared.models.base import AuditModel


class Term(AuditModel):
    """
    Represents an abstract academic period within a term type.

    Examples:
        - T1, T2, T3 (for Trimester)
        - S1, S2 (for Semester)
        - Q1, Q2, Q3, Q4 (for Quarter)

    Business Rules:
        - Code must be unique within a term type
        - Order must be unique within a term type
        - Order must be between 1 and term_type.period_count
        - No concrete dates (managed by SchoolYearCycleTerm)
        - Cannot be physically deleted if used in school year cycle terms
    """

    term_type = models.ForeignKey(
        "academic.TermType",
        on_delete=models.PROTECT,
        related_name="terms",
        help_text="Type de découpage associé",
    )
    code = models.CharField(
        max_length=10,
        help_text="Code court (ex. T1, T2, S1, S2)",
    )
    name = models.CharField(
        max_length=100,
        blank=True,
        help_text="Nom lisible (ex. Trimestre 1, Semestre 1)",
    )
    order = models.PositiveIntegerField(
        help_text="Position dans le TermType (1..n)",
    )

    class Meta:
        db_table = "term"
        verbose_name = "Term"
        verbose_name_plural = "Terms"
        ordering = ["term_type", "order"]
        indexes = [
            models.Index(fields=["term_type", "order"], name="term_type_order_idx"),
            models.Index(fields=["term_type", "code"], name="term_type_code_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["term_type", "code"],
                condition=models.Q(is_deleted=False),
                name="unique_term_code_per_type",
            ),
            models.UniqueConstraint(
                fields=["term_type", "order"],
                condition=models.Q(is_deleted=False),
                name="unique_term_order_per_type",
            ),
            models.CheckConstraint(
                condition=models.Q(order__gt=0),
                name="term_order_positive",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}" if self.name else self.code

    def clean(self):
        """Validate model fields."""
        super().clean()

        # Order must be > 0
        if self.order <= 0:
            raise ValidationError(
                {"order": "Order must be greater than 0"}
            )

        # Order must not exceed term_type.period_count
        if self.term_type and self.order > self.term_type.period_count:
            raise ValidationError(
                {
                    "order": f"Order cannot exceed {self.term_type.period_count} "
                    f"for term type '{self.term_type}'"
                }
            )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
