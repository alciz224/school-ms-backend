"""
Cycle service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.academic.models import Cycle


class CycleService:
    """Service for cycle operations."""

    @staticmethod
    def create(*, code: str, name: str, has_track: bool = False, user=None) -> Cycle:
        """
        Create a new cycle.

        Args:
            code: Cycle code (e.g., "PRI", "COL")
            name: Cycle name (e.g., "Primaire", "Collège")
            has_track: Whether cycle supports tracks/specializations
            user: User performing the action

        Returns:
            Created Cycle instance
        """
        cycle = Cycle(
            code=code.upper().strip(),
            name=name.strip(),
            has_track=has_track,
            created_by=user
        )
        cycle.save()
        return cycle

    @staticmethod
    def update(*, cycle: Cycle, code: str = None, name: str = None, 
               has_track: bool = None, user=None) -> Cycle:
        """
        Update a cycle.

        Args:
            cycle: Cycle instance to update
            code: New code (optional)
            name: New name (optional)
            has_track: New has_track value (optional)
            user: User performing the action

        Returns:
            Updated Cycle instance

        Raises:
            ValidationError: If has_track change would violate constraints
        """
        # If changing has_track, validate existing tracks/levels
        if has_track is not None and has_track != cycle.has_track:
            if not has_track and cycle.tracks.filter(is_deleted=False).exists():
                raise ValidationError(
                    _("Cannot disable tracks for cycle that has existing tracks. "
                      "Delete all tracks first.")
                )
            if not has_track and cycle.levels.filter(
                is_deleted=False, track__isnull=False
            ).exists():
                raise ValidationError(
                    _("Cannot disable tracks for cycle that has levels with tracks. "
                      "Update or delete affected levels first.")
                )

        if code is not None:
            cycle.code = code.upper().strip()
        if name is not None:
            cycle.name = name.strip()
        if has_track is not None:
            cycle.has_track = has_track
            
        cycle.updated_by = user
        cycle.save()
        return cycle

    @staticmethod
    def delete(*, cycle: Cycle, user=None, hard: bool = False) -> None:
        """
        Delete a cycle (soft delete by default).

        Args:
            cycle: Cycle instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If cycle has dependencies
        """
        # Check for tracks
        if cycle.tracks.filter(is_deleted=False).exists():
            raise ValidationError(
                _("Cannot delete cycle with existing tracks. "
                  "Delete all tracks first.")
            )

        # Check for levels
        if cycle.levels.filter(is_deleted=False).exists():
            raise ValidationError(
                _("Cannot delete cycle with existing levels. "
                  "Delete all levels first.")
            )

        # TODO: Check for school year cycles when implemented

        if hard:
            cycle.hard_delete()
        else:
            cycle.deleted_by = user
            cycle.delete()  # Uses soft delete

    @staticmethod
    def restore(*, cycle: Cycle, user=None) -> Cycle:
        """
        Restore a soft-deleted cycle.

        Args:
            cycle: Cycle instance to restore
            user: User performing the action

        Returns:
            Restored Cycle instance
        """
        cycle.is_deleted = False
        cycle.deleted_at = None
        cycle.deleted_by = None
        cycle.updated_by = user
        cycle.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by", "updated_at", "updated_by"
        ])
        
        return cycle