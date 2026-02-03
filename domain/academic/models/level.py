"""Level model."""
from django.core.exceptions import ValidationError
from django.db import models

from domain.shared.models.base import AuditModel


class Level(AuditModel):
    """
    Represents a specific educational level within a cycle.

    Examples:
        - 1ère année (Primaire)
        - 2ème année (Primaire)
        - Terminale SM (Lycée - Sciences Math track)
        - Terminale SS (Lycée - Sciences Sociales track)

    Business Rules:
        - Code and name must be unique within a cycle
        - track_id is required if cycle.has_track = True
        - order defines progression within the cycle
        - Cannot be physically deleted if used in school year levels
    """

    code = models.CharField(
        max_length=20,
        help_text="Code court (ex. 1A, 2A, TER_SM)",
    )
    name = models.CharField(
        max_length=100,
        help_text="Nom lisible (ex. 1ère année, Terminale SM)",
    )
    cycle = models.ForeignKey(
        "academic.Cycle",
        on_delete=models.PROTECT,
        related_name="levels",
        help_text="Cycle associé",
    )
    track = models.ForeignKey(
        "academic.Track",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="levels",
        help_text="Filière optionnelle si le cycle a des options",
    )
    order = models.PositiveIntegerField(
        help_text="Ordre dans le cycle (ex. 1, 2, 3...)",
    )

    class Meta:
        db_table = "level"
        verbose_name = "Level"
        verbose_name_plural = "Levels"
        ordering = ["cycle", "order"]
        indexes = [
            models.Index(fields=["cycle", "order"], name="level_cycle_order_idx"),
            models.Index(fields=["cycle", "track"], name="level_cycle_track_idx"),
            models.Index(fields=["cycle", "code"], name="level_cycle_code_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["cycle", "code"],
                condition=models.Q(is_deleted=False),
                name="unique_level_code_per_cycle",
            ),
            models.UniqueConstraint(
                fields=["cycle", "name"],
                condition=models.Q(is_deleted=False),
                name="unique_level_name_per_cycle",
            ),
        ]

    def __str__(self):
        if self.track:
            return f"{self.name} - {self.track.code}"
        return self.name

    def clean(self):
        """Validate model fields."""
        super().clean()

        # If cycle has tracks, track_id is required
        if self.cycle and self.cycle.has_track and not self.track:
            raise ValidationError(
                {"track": f"Track is required for cycle '{self.cycle}'"}
            )

        # If cycle doesn't have tracks, track_id should be null
        if self.cycle and not self.cycle.has_track and self.track:
            raise ValidationError(
                {"track": f"Cycle '{self.cycle}' does not support tracks"}
            )

        # Validate track belongs to the same cycle
        if self.track and self.track.cycle_id != self.cycle_id:
            raise ValidationError(
                {"track": "Track must belong to the same cycle"}
            )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)
