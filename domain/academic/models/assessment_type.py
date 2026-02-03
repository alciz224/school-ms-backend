"""AssessmentType model."""
from django.db import models

from domain.shared.models.base import AuditModel


class AssessmentType(AuditModel):
    """
    Represents a type of academic evaluation (global reference).

    Examples:
        - Composition (formal exam)
        - Note de cours (classwork grade)
        - Participation (participation grade)
        - Devoir (homework)

    Business Rules:
        - Code and name must be globally unique
        - Cannot be physically deleted if used in assessments
        - Active/inactive status managed per cycle assessment, not here
    """

    code = models.CharField(
        max_length=20,
        help_text="Code court (ex. COMPO, COURS, PART)",
        db_index=True,
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom lisible (ex. Composition, Note de cours)",
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        help_text="Description détaillée du type d'évaluation",
    )

    class Meta:
        db_table = "assessment_type"
        verbose_name = "Assessment Type"
        verbose_name_plural = "Assessment Types"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_assessment_type_code",
            ),
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(is_deleted=False),
                name="unique_assessment_type_name",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
