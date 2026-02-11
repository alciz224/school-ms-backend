from django.db import transaction

from domain.assessment.constants import (
    ASSESSMENT_SUBJECT_STATUS_TRANSITIONS,
    AssessmentSubjectStatus,
)
from domain.assessment.models import AssessmentSubject
from domain.shared.exceptions import BusinessRuleException


class AssessmentSubjectService:
    @staticmethod
    @transaction.atomic
    def transition(*, obj: AssessmentSubject, to_status: str, user=None) -> AssessmentSubject:
        if to_status not in ASSESSMENT_SUBJECT_STATUS_TRANSITIONS.get(obj.status, []):
            raise BusinessRuleException(rule="invalid_transition", message=f"Cannot transition {obj.status} → {to_status}")
        obj.status = to_status
        obj.save_by(user=user)
        return obj

    @staticmethod
    def publish(*, obj: AssessmentSubject, user=None) -> AssessmentSubject:
        return AssessmentSubjectService.transition(obj=obj, to_status=AssessmentSubjectStatus.PUBLISHED, user=user)

    @staticmethod
    def close(*, obj: AssessmentSubject, user=None) -> AssessmentSubject:
        return AssessmentSubjectService.transition(obj=obj, to_status=AssessmentSubjectStatus.CLOSED, user=user)

    @staticmethod
    def archive(*, obj: AssessmentSubject, user=None) -> AssessmentSubject:
        return AssessmentSubjectService.transition(obj=obj, to_status=AssessmentSubjectStatus.ARCHIVED, user=user)
