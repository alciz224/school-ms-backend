"""AssessmentType service - basic implementation."""

from domain.academic.models import AssessmentType

class AssessmentTypeService:
    """Service for assessment type operations."""

    @staticmethod
    def create(*, code: str, name: str, user=None) -> AssessmentType:
        assessment_type = AssessmentType(code=code.strip(), name=name.strip(), created_by=user)
        assessment_type.save()
        return assessment_type

    @staticmethod
    def update(*, assessment_type: AssessmentType, code: str = None, name: str = None, user=None) -> AssessmentType:
        if code: assessment_type.code = code.strip()
        if name: assessment_type.name = name.strip()
        assessment_type.updated_by = user
        assessment_type.save()
        return assessment_type

    @staticmethod
    def delete(*, assessment_type: AssessmentType, user=None, hard: bool = False) -> None:
        if hard:
            assessment_type.hard_delete()
        else:
            assessment_type.deleted_by = user
            assessment_type.delete()