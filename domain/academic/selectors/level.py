"""
Level selectors.
"""

from django.db.models import QuerySet, Q
from typing import Optional

from domain.academic.models import Level, Cycle, Track


class LevelSelector:
    """Selector for level queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Level]:
        """
        Get all levels.

        Args:
            include_deleted: If True, include soft-deleted levels

        Returns:
            QuerySet of levels
        """
        if include_deleted:
            return Level.all_objects.all()
        return Level.objects.all()

    @staticmethod
    def get_by_id(*, level_id: int, include_deleted: bool = False) -> Optional[Level]:
        """
        Get a level by ID.

        Args:
            level_id: Level ID
            include_deleted: If True, include soft-deleted levels

        Returns:
            Level instance or None
        """
        manager = Level.all_objects if include_deleted else Level.objects
        return manager.filter(id=level_id).first()

    @staticmethod
    def for_cycle(*, cycle: Cycle, include_deleted: bool = False) -> QuerySet[Level]:
        """
        Get levels for a specific cycle.

        Args:
            cycle: Cycle instance
            include_deleted: If True, include soft-deleted levels

        Returns:
            QuerySet of levels for the cycle
        """
        manager = Level.all_objects if include_deleted else Level.objects
        return manager.filter(cycle=cycle).order_by('order')

    @staticmethod
    def for_track(*, track: Track, include_deleted: bool = False) -> QuerySet[Level]:
        """
        Get levels for a specific track.

        Args:
            track: Track instance
            include_deleted: If True, include soft-deleted levels

        Returns:
            QuerySet of levels for the track
        """
        manager = Level.all_objects if include_deleted else Level.objects
        return manager.filter(track=track).order_by('order')

    @staticmethod
    def for_cycle_and_track(*, cycle: Cycle, track: Track = None, 
                           include_deleted: bool = False) -> QuerySet[Level]:
        """
        Get levels for a specific cycle and optional track.

        Args:
            cycle: Cycle instance
            track: Track instance (optional)
            include_deleted: If True, include soft-deleted levels

        Returns:
            QuerySet of levels
        """
        manager = Level.all_objects if include_deleted else Level.objects
        queryset = manager.filter(cycle=cycle)
        
        if track is not None:
            queryset = queryset.filter(track=track)
        elif cycle.has_track:
            # If cycle has tracks but no specific track requested, 
            # return levels without tracks only
            queryset = queryset.filter(track__isnull=True)
            
        return queryset.order_by('order')

    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[Level]:
        """
        Search levels by name or code.

        Args:
            query: Search query
            include_deleted: If True, include soft-deleted levels

        Returns:
            QuerySet of matching levels
        """
        manager = Level.all_objects if include_deleted else Level.objects
        return manager.filter(
            Q(name__icontains=query) | Q(code__icontains=query)
        )

    @staticmethod
    def get_by_code_and_cycle(*, code: str, cycle: Cycle, 
                             include_deleted: bool = False) -> Optional[Level]:
        """
        Get a level by code within a specific cycle.

        Args:
            code: Level code
            cycle: Cycle instance
            include_deleted: If True, include soft-deleted levels

        Returns:
            Level instance or None
        """
        manager = Level.all_objects if include_deleted else Level.objects
        return manager.filter(code__iexact=code.strip(), cycle=cycle).first()

    @staticmethod
    def get_max_order_in_cycle(*, cycle: Cycle, track: Track = None) -> int:
        """
        Get the maximum order value for levels in a cycle (and optional track).

        Args:
            cycle: Cycle instance
            track: Track instance (optional)

        Returns:
            Maximum order value or 0 if no levels
        """
        queryset = Level.objects.filter(cycle=cycle)
        
        if track is not None:
            queryset = queryset.filter(track=track)
            
        max_order = queryset.aggregate(
            max_order=models.Max('order')
        )['max_order']
        
        return max_order or 0

    @staticmethod
    def exists_in_cycle(*, code: str, cycle: Cycle, exclude_id: int = None) -> bool:
        """
        Check if a level with given code exists in the cycle.

        Args:
            code: Level code to check
            cycle: Cycle instance
            exclude_id: Exclude level with this ID

        Returns:
            True if level exists with the code in the cycle
        """
        queryset = Level.objects.filter(code__iexact=code.strip(), cycle=cycle)
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset.exists()

    @staticmethod
    def get_without_track(*, cycle: Cycle) -> QuerySet[Level]:
        """
        Get levels in a cycle that don't have a track assigned.

        Args:
            cycle: Cycle instance

        Returns:
            QuerySet of levels without tracks
        """
        return Level.objects.filter(cycle=cycle, track__isnull=True)

    @staticmethod
    def get_with_track(*, cycle: Cycle) -> QuerySet[Level]:
        """
        Get levels in a cycle that have a track assigned.

        Args:
            cycle: Cycle instance

        Returns:
            QuerySet of levels with tracks
        """
        return Level.objects.filter(cycle=cycle, track__isnull=False)


# Import models for aggregation
from django.db import models