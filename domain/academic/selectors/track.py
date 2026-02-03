"""Track selectors - basic implementation."""

from django.db.models import QuerySet
from typing import Optional
from domain.academic.models import Track

class TrackSelector:
    """Selector for track queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Track]:
        return Track.all_objects.all() if include_deleted else Track.objects.all()

    @staticmethod
    def get_by_id(*, track_id: int, include_deleted: bool = False) -> Optional[Track]:
        manager = Track.all_objects if include_deleted else Track.objects
        return manager.filter(id=track_id).first()

    @staticmethod
    def for_cycle(*, cycle, include_deleted: bool = False) -> QuerySet[Track]:
        manager = Track.all_objects if include_deleted else Track.objects
        return manager.filter(cycle=cycle)