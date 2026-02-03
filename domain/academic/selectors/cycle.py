"""
Cycle selectors.
"""

from django.db.models import QuerySet, Count, Q
from typing import Optional

from domain.academic.models import Cycle


class CycleSelector:
    """Selector for cycle queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Cycle]:
        """
        Get all cycles.

        Args:
            include_deleted: If True, include soft-deleted cycles

        Returns:
            QuerySet of cycles
        """
        if include_deleted:
            return Cycle.all_objects.all()
        return Cycle.objects.all()

    @staticmethod
    def get_by_id(*, cycle_id: int, include_deleted: bool = False) -> Optional[Cycle]:
        """
        Get a cycle by ID.

        Args:
            cycle_id: Cycle ID
            include_deleted: If True, include soft-deleted cycles

        Returns:
            Cycle instance or None
        """
        manager = Cycle.all_objects if include_deleted else Cycle.objects
        return manager.filter(id=cycle_id).first()

    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[Cycle]:
        """
        Get a cycle by code.

        Args:
            code: Cycle code
            include_deleted: If True, include soft-deleted cycles

        Returns:
            Cycle instance or None
        """
        manager = Cycle.all_objects if include_deleted else Cycle.objects
        return manager.filter(code__iexact=code.strip()).first()

    @staticmethod
    def with_tracks() -> QuerySet[Cycle]:
        """
        Get cycles that support tracks/specializations.

        Returns:
            QuerySet of cycles with has_track=True
        """
        return Cycle.objects.with_tracks()

    @staticmethod
    def without_tracks() -> QuerySet[Cycle]:
        """
        Get cycles that don't support tracks.

        Returns:
            QuerySet of cycles with has_track=False
        """
        return Cycle.objects.without_tracks()

    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[Cycle]:
        """
        Search cycles by name or code.

        Args:
            query: Search query
            include_deleted: If True, include soft-deleted cycles

        Returns:
            QuerySet of matching cycles
        """
        manager = Cycle.all_objects if include_deleted else Cycle.objects
        return manager.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )

    @staticmethod
    def get_with_track_counts() -> QuerySet[Cycle]:
        """
        Get all cycles with their track counts.

        Returns:
            QuerySet of cycles annotated with track_count
        """
        return Cycle.objects.annotate(
            track_count=Count('tracks', filter=Q(tracks__is_deleted=False))
        )

    @staticmethod
    def get_with_level_counts() -> QuerySet[Cycle]:
        """
        Get all cycles with their level counts.

        Returns:
            QuerySet of cycles annotated with level_count
        """
        return Cycle.objects.annotate(
            level_count=Count('levels', filter=Q(levels__is_deleted=False))
        )

    @staticmethod
    def get_with_stats() -> QuerySet[Cycle]:
        """
        Get all cycles with track and level counts.

        Returns:
            QuerySet of cycles annotated with track_count and level_count
        """
        return Cycle.objects.annotate(
            track_count=Count('tracks', filter=Q(tracks__is_deleted=False)),
            level_count=Count('levels', filter=Q(levels__is_deleted=False))
        )

    @staticmethod
    def exists_by_code(*, code: str, exclude_id: int = None) -> bool:
        """
        Check if a cycle exists with the given code.

        Args:
            code: Cycle code to check
            exclude_id: Exclude cycle with this ID

        Returns:
            True if cycle exists with the code
        """
        queryset = Cycle.objects.filter(code__iexact=code.strip())
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset.exists()

    @staticmethod
    def exists_by_name(*, name: str, exclude_id: int = None) -> bool:
        """
        Check if a cycle exists with the given name.

        Args:
            name: Cycle name to check
            exclude_id: Exclude cycle with this ID

        Returns:
            True if cycle exists with the name
        """
        queryset = Cycle.objects.filter(name__iexact=name.strip())
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset.exists()