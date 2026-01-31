"""SchoolYearLevel model."""
from django.core.exceptions import ValidationError
from django.db import models

from domain.academic.models import Level, Track
from domain.school_operations.models.school_year_cycle import SchoolYearCycle
from domain.shared.models.base import AuditModel


class SchoolYearLevel(AuditModel):
    """
    Represents a specific level within a cycle for a school year.

    Links a master Level to a SchoolYearCycle and optionally a Track if the cycle
    requires it. Serves as a container for subjects (SchoolYearLevelSubject) and
    classrooms (Classroom).

    Business Rules:
        - Each (school_year_cycle, level, track) combination must be unique
        - track_id is required if the level's cycle has has_track = True
        - Cannot be deleted if classrooms, subjects, or enrollments are associated
        - Immutable once classrooms or subjects are created

    Examples:
        - School Year 2024-2025, Primaire, 1ère année (no track)
        - School Year 2024-2025, Lycée, Terminale, SM track
    """

    school_year_cycle = models.ForeignKey(
        SchoolYearCycle,
        on_delete=models.PROTECT,
        related_name="levels",
        help_text="Cycle de l'année scolaire associé",
    )
    level = models.ForeignKey(
        Level,
        on_delete=models.PROTECT,
        related_name="school_year_levels",
        help_text="Niveau MASTER associé",
    )
    track = models.ForeignKey(
        Track,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="school_year_levels",
        help_text="Filière/option si le cycle en nécessite",
    )

    class Meta:
        db_table = "school_year_level"
        verbose_name = "School Year Level"
        verbose_name_plural = "School Year Levels"
        ordering = ["school_year_cycle", "level__order"]
        indexes = [
            models.Index(
                fields=["school_year_cycle", "level"],
                name="syl_syc_level_idx",
            ),
            models.Index(
                fields=["school_year_cycle", "track"],
                name="syl_syc_track_idx",
            ),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year_cycle", "level", "track"],
                condition=models.Q(is_deleted=False),
                name="unique_school_year_level",
            ),
        ]

    def __str__(self):
        if self.track:
            return f"{self.school_year_cycle.school_year} - {self.level} - {self.track}"
        return f"{self.school_year_cycle.school_year} - {self.level}"

    def clean(self):
        """Validate model fields and business rules."""
        super().clean()

        # Validate that level belongs to the same cycle as school_year_cycle
        if self.level_id and self.school_year_cycle_id:
            if self.level.cycle_id != self.school_year_cycle.cycle_id:
                raise ValidationError(
                    {
                        "level": f"Level must belong to the cycle '{self.school_year_cycle.cycle}'"
                    }
                )

        # Validate track requirements
        if self.level_id and self.school_year_cycle_id:
            cycle_has_track = self.school_year_cycle.cycle.has_track

            # If cycle has tracks, track is required
            if cycle_has_track and not self.track_id:
                raise ValidationError(
                    {"track": f"Track is required for cycle '{self.school_year_cycle.cycle}'"}
                )

            # If cycle doesn't have tracks, track should be null
            if not cycle_has_track and self.track_id:
                raise ValidationError(
                    {"track": f"Cycle '{self.school_year_cycle.cycle}' does not support tracks"}
                )

        # Validate track belongs to the same cycle
        if self.track_id and self.school_year_cycle_id:
            if self.track.cycle_id != self.school_year_cycle.cycle_id:
                raise ValidationError(
                    {"track": "Track must belong to the same cycle"}
                )

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    def can_delete(self):
        """
        Check if the level can be deleted.

        Returns:
            bool: True if can be deleted, False otherwise
        """
        # Check if there are associated classrooms (when implemented)
        # if self.classrooms.exists():
        #     return False

        # Check if there are associated subjects (when implemented)
        # if self.subjects.exists():
        #     return False

        # Check if there are associated enrollments (when implemented)
        # if self.enrollments.exists():
        #     return False

        return True

    def get_classrooms(self):
        """
        Get all classrooms associated with this level.

        Returns:
            QuerySet: Classroom queryset (when implemented)
        """
        # Placeholder for when Classroom is implemented
        # return self.classrooms.filter(is_deleted=False)
        return None

    def get_subjects(self):
        """
        Get all subjects associated with this level.

        Returns:
            QuerySet: SchoolYearLevelSubject queryset (when implemented)
        """
        # Placeholder for when SchoolYearLevelSubject is implemented
        # return self.subjects.filter(is_deleted=False)
        return None
