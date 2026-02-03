"""Track model."""
from django.core.exceptions import ValidationError
from django.db import models

from domain.shared.models.base import AuditModel


class Track(AuditModel):
    """
    Represents a specialization or option within a cycle.

    Examples:
        - Sciences Mathématiques (SM)
        - Sciences Expérimentales (SE)
        - Sciences Sociales (SS)
        - Lettres (L)

    Business Rules:
        - Can only exist for cycles with has_track = True
        - Code and name must be unique within a cycle
        - Cannot be physically deleted if used in levels
    """

    code = models.CharField(
        max_length=10,
        help_text="Code court (ex. SM, SS, SE, L)",
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom lisible (ex. Sciences Mathématiques)",
    )
    cycle = models.ForeignKey(
        "academic.Cycle",
        on_delete=models.PROTECT,
        related_name="tracks",
        help_text="Cycle auquel la track appartient",
    )

    class Meta:
        db_table = "track"
        verbose_name = "Track"
        verbose_name_plural = "Tracks"
        ordering = ["cycle", "code"]
        indexes = [
            models.Index(fields=["cycle", "code"], name="track_cycle_code_idx"),
            models.Index(fields=["cycle", "name"], name="track_cycle_name_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["cycle", "code"],
                condition=models.Q(is_deleted=False),
                name="unique_track_code_per_cycle",
            ),
            models.UniqueConstraint(
                fields=["cycle", "name"],
                condition=models.Q(is_deleted=False),
                name="unique_track_name_per_cycle",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.code})"

    def clean(self):
        """Validate model fields."""
        super().clean()

        # Track can only exist if cycle has_track = True
        if self.cycle and not self.cycle.has_track:
            raise ValidationError(
                {"cycle": f"Cycle '{self.cycle}' does not support tracks"}
            )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
