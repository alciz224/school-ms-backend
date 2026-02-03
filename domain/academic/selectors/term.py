"""Term selectors - basic implementation."""

from django.db.models import QuerySet
from typing import Optional
from domain.academic.models import Term

class TermSelector:
    """Selector for term queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Term]:
        return Term.all_objects.all() if include_deleted else Term.objects.all()

    @staticmethod
    def get_by_id(*, term_id: int, include_deleted: bool = False) -> Optional[Term]:
        manager = Term.all_objects if include_deleted else Term.objects
        return manager.filter(id=term_id).first()

    @staticmethod
    def for_term_type(*, term_type, include_deleted: bool = False) -> QuerySet[Term]:
        manager = Term.all_objects if include_deleted else Term.objects
        return manager.filter(term_type=term_type).order_by('order')