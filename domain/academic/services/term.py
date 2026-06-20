"""Term service - basic implementation."""

from domain.academic.models import Term

class TermService:
    """Service for term operations."""

    @staticmethod
    def create(*, code: str, name: str, term_type, order: int, user=None) -> Term:
        term = Term(code=code.upper().strip(), name=name.strip(), term_type=term_type, order=order, created_by=user)
        term.save()
        return term

    @staticmethod
    def update(*, term: Term, code: str = None, name: str = None, order: int = None, user=None) -> Term:
        if code: term.code = code.upper().strip()
        if name: term.name = name.strip()
        if order is not None: term.order = order
        term.updated_by = user
        term.save()
        return term

    @staticmethod
    def delete(*, term: Term, user=None, hard: bool = False) -> None:
        if hard:
            term.hard_delete()
        else:
            term.deleted_by = user
            term.delete()