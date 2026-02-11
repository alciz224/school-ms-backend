from __future__ import annotations

from datetime import date

from django.db import transaction
from django.db.models import Max

from domain.enrollment.models import Classroom, StudentEnrollment
from domain.enrollment.models.constants import StudentEnrollmentStatus
from domain.shared.exceptions import BusinessRuleException, ValidationException


class StudentEnrollmentService:
    @staticmethod
    def _ensure_classroom_suffix(*, obj: StudentEnrollment, user=None) -> None:
        """Assign/normalize suffix according to rule (A).

        - If no classroom: clear suffix.
        - If classroom exists and no collision: suffix stays NULL.
        - If collision: first becomes 1, next 2, etc.

        Note: This method expects to be called inside an atomic transaction when assigning.
        """

        if not obj.classroom_id:
            obj.classroom_suffix = None
            return

        # Lock all same-name rows in classroom to avoid concurrent suffix assignment.
        same_name_qs = (
            StudentEnrollment.objects.select_for_update()
            .filter(
                classroom_id=obj.classroom_id,
                first_name=obj.first_name,
                last_name=obj.last_name,
                is_deleted=False,
            )
        )

        # Exclude current object if already persisted
        if obj.pk:
            same_name_qs = same_name_qs.exclude(pk=obj.pk)

        existing_count = same_name_qs.count()
        if existing_count == 0:
            obj.classroom_suffix = None
            return

        # Collision exists: ensure existing "first" has suffix=1 if it doesn't already.
        first_without_suffix = same_name_qs.filter(classroom_suffix__isnull=True).order_by("created_at").first()
        if first_without_suffix is not None:
            first_without_suffix.classroom_suffix = 1
            first_without_suffix.save_by(user=user)

        max_suffix = same_name_qs.aggregate(m=Max("classroom_suffix"))["m"] or 1
        # New one should be next integer
        obj.classroom_suffix = max_suffix + 1
    @staticmethod
    @transaction.atomic
    def create(
        *,
        student=None,
        first_name: str,
        last_name: str,
        school_year_level,
        enrollment_date: date,
        annual_identifier: str,
        classroom: Classroom | None = None,
        classroom_identifier: str | None = None,
        enrollment_status: str = StudentEnrollmentStatus.PRE_REGISTERED,
        start_date: date | None = None,
        user=None,
    ) -> StudentEnrollment:
        obj = StudentEnrollment(
            student=student,
            first_name=first_name,
            last_name=last_name,
            school_year_level=school_year_level,
            classroom=classroom,
            enrollment_status=enrollment_status,
            enrollment_date=enrollment_date,
            start_date=start_date,
            annual_identifier=annual_identifier,
            classroom_identifier=classroom_identifier,
        )

        # Assign suffix if needed.
        StudentEnrollmentService._ensure_classroom_suffix(obj=obj, user=user)

        obj.save_by(user=user)
        return obj

    @staticmethod
    @transaction.atomic
    def update(
        *,
        obj: StudentEnrollment,
        classroom: Classroom | None = None,
        enrollment_status: str | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        transfer_reason: str | None = None,
        classroom_identifier: str | None = None,
        user=None,
    ) -> StudentEnrollment:
        classroom_changed = False
        if classroom is not None and classroom.id != obj.classroom_id:
            obj.classroom = classroom
            obj.classroom_suffix = None
            classroom_changed = True
        if enrollment_status is not None:
            obj.enrollment_status = enrollment_status
        if start_date is not None:
            obj.start_date = start_date
        if end_date is not None:
            obj.end_date = end_date
        if transfer_reason is not None:
            obj.transfer_reason = transfer_reason
        if classroom_identifier is not None:
            obj.classroom_identifier = classroom_identifier

        if classroom_changed:
            StudentEnrollmentService._ensure_classroom_suffix(obj=obj, user=user)

        obj.save_by(user=user)
        return obj

    @staticmethod
    @transaction.atomic
    def transfer(
        *,
        obj: StudentEnrollment,
        to_classroom: Classroom,
        transfer_date: date | None = None,
        transfer_reason: str | None = None,
        classroom_identifier: str | None = None,
        user=None,
    ) -> StudentEnrollment:
        """Transfer a student enrollment to another classroom (same SchoolYearLevel)."""

        if obj.is_deleted:
            raise BusinessRuleException(rule="cannot_transfer_deleted")

        if obj.enrollment_status not in [StudentEnrollmentStatus.ACTIVE, StudentEnrollmentStatus.PRE_REGISTERED]:
            raise BusinessRuleException(rule="cannot_transfer_in_status")

        if obj.school_year_level_id != to_classroom.school_year_level_id:
            raise ValidationException(
                message="Target classroom must belong to the same SchoolYearLevel.",
                field_errors={"to_classroom": ["must_belong_to_same_school_year_level"]},
            )

        # lock row to prevent concurrent transfers
        obj = StudentEnrollment.objects.select_for_update().get(id=obj.id)

        obj.previous_classroom = obj.classroom
        obj.classroom = to_classroom
        obj.classroom_suffix = None  # will be computed if collision
        if transfer_reason is not None:
            obj.transfer_reason = transfer_reason
        if transfer_date is not None:
            obj.start_date = transfer_date
        if classroom_identifier is not None:
            obj.classroom_identifier = classroom_identifier

        # if student was pre-registered, moving to a classroom can activate them
        if obj.enrollment_status == StudentEnrollmentStatus.PRE_REGISTERED:
            obj.enrollment_status = StudentEnrollmentStatus.ACTIVE

        # Assign suffix in the destination classroom if needed.
        StudentEnrollmentService._ensure_classroom_suffix(obj=obj, user=user)

        obj.save_by(user=user)
        return obj
