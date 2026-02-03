"""Cycle model."""
from django.db import models

from domain.shared.models.base import AuditModel


class Cycle(AuditModel):
    """
    Represents an educational cycle (global reference).

    Examples:
        - Maternelle (Kindergarten)
        - Primaire (Primary)
        - Collège (Middle School)
        - Lycée (High School)

    Business Rules:
        - Code and name must be unique
        - has_track indicates if the cycle supports specializations
        - Cannot be physically deleted if used in levels or school years
    """

    code = models.CharField(
        max_length=10,
        help_text="Code court (ex. MAT, PRI, COL, LYC)",
        db_index=True,
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom lisible (ex. Maternelle, Primaire)",
        db_index=True,
    )
    has_track = models.BooleanField(
        default=False,
        help_text="Indique si le cycle peut avoir des options/tracks",
    )

    class Meta:
        db_table = "cycle"
        verbose_name = "Cycle"
        verbose_name_plural = "Cycles"
        ordering = ["code"]
        indexes = [
            models.Index(fields=["has_track", "code"], name="cycle_has_track_code_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(is_deleted=False),
                name="unique_cycle_code",
            ),
            models.UniqueConstraint(
                fields=["name"],
                condition=models.Q(is_deleted=False),
                name="unique_cycle_name",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"
