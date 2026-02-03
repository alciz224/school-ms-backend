"""TermType selectors - basic implementation."""

from django.db.models import QuerySet
from typing import Optional
from domain.academic.models import TermType

class TermTypeSelector:
    """Selector for term type queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[TermType]:
        return TermType.all_objects.all() if include_deleted else TermType.objects.all()

    @staticmethod
    def get_by_id(*, term_type_id: int, include_deleted: bool = False) -> Optional[TermType]:
        manager = TermType.all_objects if include_deleted else TermType.objects
        return manager.filter(id=term_type_id).first()

    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[TermType]:
        manager = TermType.all_objects if include_deleted else TermType.objects
        return manager.filter(code__iexact=code.strip()).first()