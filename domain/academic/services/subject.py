"""Subject service - basic implementation."""

from domain.academic.models import Subject

class SubjectService:
    """Service for subject operations."""

    @staticmethod
    def create(*, code: str, name: str, user=None) -> Subject:
        subject = Subject(code=code.strip(), name=name.strip(), created_by=user)
        subject.save()
        return subject

    @staticmethod
    def update(*, subject: Subject, code: str = None, name: str = None, user=None) -> Subject:
        if code: subject.code = code.strip()
        if name: subject.name = name.strip()
        subject.updated_by = user
        subject.save()
        return subject

    @staticmethod
    def delete(*, subject: Subject, user=None, hard: bool = False) -> None:
        if hard:
            subject.hard_delete()
        else:
            subject.deleted_by = user
            subject.delete()