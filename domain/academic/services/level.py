"""
Level service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.academic.models import Level, Cycle, Track


class LevelService:
    """Service for level operations."""

    @staticmethod
    def create(*, code: str, name: str, cycle: Cycle, track: Track = None, 
               order: int, user=None) -> Level:
        """
        Create a new level.

        Args:
            code: Level code (e.g., "1A", "TER_SM")
            name: Level name (e.g., "1ère année", "Terminale SM")
            cycle: Associated cycle
            track: Associated track (if cycle supports tracks)
            order: Order within the cycle
            user: User performing the action

        Returns:
            Created Level instance

        Raises:
            ValidationError: If track requirements are not met
        """
        level = Level(
            code=code.strip(),
            name=name.strip(),
            cycle=cycle,
            track=track,
            order=order,
            created_by=user
        )
        # save() will handle cycle-track validation
        level.save()
        return level

    @staticmethod
    def update(*, level: Level, code: str = None, name: str = None, 
               cycle: Cycle = None, track: Track = None, order: int = None,
               user=None) -> Level:
        """
        Update a level.

        Args:
            level: Level instance to update
            code: New code (optional)
            name: New name (optional)
            cycle: New cycle (optional)
            track: New track (optional)
            order: New order (optional)
            user: User performing the action

        Returns:
            Updated Level instance

        Raises:
            ValidationError: If changes violate business rules
        """
        if code is not None:
            level.code = code.strip()
        if name is not None:
            level.name = name.strip()
        if cycle is not None:
            level.cycle = cycle
        if track is not None:
            level.track = track
        if order is not None:
            level.order = order
            
        level.updated_by = user
        # save() will handle validation
        level.save()
        return level

    @staticmethod
    def delete(*, level: Level, user=None, hard: bool = False) -> None:
        """
        Delete a level (soft delete by default).

        Args:
            level: Level instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If level has dependencies
        """
        # Check for school year levels
        from domain.school_operations.models import SchoolYearLevel
        if SchoolYearLevel.objects.filter(level=level, is_deleted=False).exists():
            raise ValidationError(
                _('Cannot delete level with associated school year levels. '
                  'Delete all school year levels first.')
            )
        
        if hard:
            level.hard_delete()
        else:
            level.deleted_by = user
            level.delete()  # Uses soft delete

    @staticmethod
    def restore(*, level: Level, user=None) -> Level:
        """
        Restore a soft-deleted level.

        Args:
            level: Level instance to restore
            user: User performing the action

        Returns:
            Restored Level instance
        """
        level.is_deleted = False
        level.deleted_at = None
        level.deleted_by = None
        level.updated_by = user
        level.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by", "updated_at", "updated_by"
        ])
        
        return level

    @staticmethod
    def reorder_levels(*, cycle: Cycle, level_orders: dict, user=None) -> list[Level]:
        """
        Reorder levels within a cycle.

        Args:
            cycle: Cycle containing the levels
            level_orders: Dict mapping level_id to new order
            user: User performing the action

        Returns:
            List of updated Level instances
        """
        updated_levels = []
        
        for level_id, new_order in level_orders.items():
            try:
                level = Level.objects.get(id=level_id, cycle=cycle)
                level.order = new_order
                level.updated_by = user
                level.save(update_fields=["order", "updated_at", "updated_by"])
                updated_levels.append(level)
            except Level.DoesNotExist:
                raise ValidationError(
                    _(f"Level with ID {level_id} not found in cycle {cycle}")
                )
        
        return updated_levels