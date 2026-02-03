"""TermType model."""
from django.core.exceptions import ValidationError
from django.db import models

from domain.shared.models.base import AuditModel


class TermType(AuditModel):
    """
    Represents a type of academic period division (global reference).

    Examples:
        - Trimester (3 periods per year)
        - Semester (2 periods per year)
        - Quarter (4 periods per year)

    Business Rules:
        - Code and name must be globally unique
        - period_count must be > 0
        - Cannot be physically deleted if used in terms or school years
        - Immutable once used in school configurations
    """

    code = models.CharField(
        max_length=20,
        help_text="Code court (ex. TRIMESTER, SEMESTER)",
        db_index=True,
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom lisible (ex. Trimestre, Semestre)",
        db_index=True,
    )
    period_count = models.PositiveIntegerField(
        help_text="Nombre de périodes (ex. 3 pour trimestre, 2 pour semestre)",
    )

    class Meta:
        db_table = "term_type"
        verbose_name = "Term Type"
        verbose_name_plural = "Term Types"
        ordering = ["period_count", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_term_type_code",
            ),
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(is_deleted=False),
                name="unique_term_type_name",
            ),
            models.CheckConstraint(
                condition=models.Q(period_count__gt=0),
                name="term_type_period_count_positive",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.period_count} periods)"

    def clean(self):
        """Validate model fields."""
        super().clean()

        if self.period_count <= 0:
            raise ValidationError(
                {"period_count": "Period count must be greater than 0"}
            )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
