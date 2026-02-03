"""Subject model."""
from django.db import models

from domain.shared.models.base import AuditModel


class Subject(AuditModel):
    """
    Represents an academic subject (global reference).

    Examples:
        - Mathématiques
        - Physique
        - Français
        - Histoire
        - Éducation Physique

    Business Rules:
        - Code and name must be globally unique
        - Cannot be physically deleted if used in school year level subjects
        - Activation/deactivation managed per school year, not here
    """

    code = models.CharField(
        max_length=20,
        help_text="Code court (ex. MATH, PHYS, FRAN)",
        db_index=True,
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom lisible (ex. Mathématiques, Physique)",
        db_index=True,
    )
    description = models.TextField(
        blank=True,
        help_text="Description facultative de la matière",
    )

    class Meta:
        db_table = "subject"
        verbose_name = "Subject"
        verbose_name_plural = "Subjects"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_subject_code",
            ),
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(is_deleted=False),
                name="unique_subject_name",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
