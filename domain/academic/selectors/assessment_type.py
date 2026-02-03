"""AssessmentType selectors - basic implementation."""

from django.db.models import QuerySet
from typing import Optional
from domain.academic.models import AssessmentType

class AssessmentTypeSelector:
    """Selector for assessment type queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[AssessmentType]:
        return AssessmentType.all_objects.all() if include_deleted else AssessmentType.objects.all()

    @staticmethod
    def get_by_id(*, assessment_type_id: int, include_deleted: bool = False) -> Optional[AssessmentType]:
        manager = AssessmentType.all_objects if include_deleted else AssessmentType.objects
        return manager.filter(id=assessment_type_id).first()

    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[AssessmentType]:
        manager = AssessmentType.all_objects if include_deleted else AssessmentType.objects
        return manager.filter(code__iexact=code.strip()).first()