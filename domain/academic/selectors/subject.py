"""Subject selectors - basic implementation."""

from django.db.models import QuerySet
from typing import Optional
from domain.academic.models import Subject

class SubjectSelector:
    """Selector for subject queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Subject]:
        return Subject.all_objects.all() if include_deleted else Subject.objects.all()

    @staticmethod
    def get_by_id(*, subject_id: int, include_deleted: bool = False) -> Optional[Subject]:
        manager = Subject.all_objects if include_deleted else Subject.objects
        return manager.filter(id=subject_id).first()

    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[Subject]:
        manager = Subject.all_objects if include_deleted else Subject.objects
        return manager.filter(code__iexact=code.strip()).first()