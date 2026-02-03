"""TermType service - basic implementation."""

from domain.academic.models import TermType

class TermTypeService:
    """Service for term type operations."""

    @staticmethod
    def create(*, code: str, name: str, period_count: int, user=None) -> TermType:
        term_type = TermType(code=code.strip(), name=name.strip(), period_count=period_count, created_by=user)
        term_type.save()
        return term_type

    @staticmethod
    def update(*, term_type: TermType, code: str = None, name: str = None, period_count: int = None, user=None) -> TermType:
        if code: term_type.code = code.strip()
        if name: term_type.name = name.strip()
        if period_count is not None: term_type.period_count = period_count
        term_type.updated_by = user
        term_type.save()
        return term_type

    @staticmethod
    def delete(*, term_type: TermType, user=None, hard: bool = False) -> None:
        if hard:
            term_type.hard_delete()
        else:
            term_type.deleted_by = user
            term_type.delete()