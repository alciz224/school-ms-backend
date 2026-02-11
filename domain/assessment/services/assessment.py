from django.db import transaction

from domain.assessment.constants import ASSESSMENT_STATUS_TRANSITIONS, AssessmentStatus
from domain.assessment.models import Assessment
from domain.shared.exceptions import BusinessRuleException


class AssessmentService:
    @staticmethod
    @transaction.atomic
    def transition(*, obj: Assessment, to_status: str, user=None) -> Assessment:
        if to_status not in ASSESSMENT_STATUS_TRANSITIONS.get(obj.status, []):
            raise BusinessRuleException(rule="invalid_transition", message=f"Cannot transition {obj.status} → {to_status}")
        obj.status = to_status
        obj.save_by(user=user)
        return obj

    @staticmethod
    def activate(*, obj: Assessment, user=None) -> Assessment:
        return AssessmentService.transition(obj=obj, to_status=AssessmentStatus.ACTIVE, user=user)

    @staticmethod
    def close(*, obj: Assessment, user=None) -> Assessment:
        return AssessmentService.transition(obj=obj, to_status=AssessmentStatus.CLOSED, user=user)

    @staticmethod
    def archive(*, obj: Assessment, user=None) -> Assessment:
        return AssessmentService.transition(obj=obj, to_status=AssessmentStatus.ARCHIVED, user=user)
