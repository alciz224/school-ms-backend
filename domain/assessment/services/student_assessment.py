from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from django.db import transaction
from django.db.models import Prefetch

from domain.assessment.models import AssessmentSubject, StudentAssessment
from domain.enrollment.models import StudentEnrollment
from domain.shared.exceptions import ValidationException, BusinessRuleException


@dataclass(frozen=True)
class BulkImportContext:
    assessment_subject: AssessmentSubject
    enrollments_by_id: Dict[int, StudentEnrollment]
    existing_by_enrollment_id: Dict[int, StudentAssessment]
    max_score: float


class StudentAssessmentService:
    @staticmethod
    def _get_bulk_import_context(*, assessment_subject_id: int) -> BulkImportContext:
        # 1) Load assessment subject with needed relations
        assessment_subject = (
            AssessmentSubject.objects.select_related(
                "assessment",
                "classroom",
                "school_year_level_subject",
            ).get(id=assessment_subject_id)
        )

        # Ensure we can accept grades
        if not assessment_subject.can_accept_grades:
            raise BusinessRuleException(
                rule="subject_not_published",
                message="Assessment subject must be PUBLISHED to accept grades.",
            )

        # 2) Load all enrollments for the classroom
        enrollments = (
            StudentEnrollment.objects.filter(
                classroom_id=assessment_subject.classroom_id,
                is_deleted=False,
            )
            .only("id", "first_name", "last_name", "classroom_id")
            .order_by("id")
        )
        enrollments_by_id = {e.id: e for e in enrollments}

        # 3) Load existing grades for this assessment subject
        existing_scores = (
            StudentAssessment.objects.filter(
                assessment_subject_id=assessment_subject_id, is_deleted=False
            )
            .only("id", "student_enrollment_id", "raw_score", "is_absent", "is_excused")
            .order_by("id")
        )
        existing_by_enrollment_id = {sa.student_enrollment_id: sa for sa in existing_scores}

        # Max score is fixed at assessment_subject level in this design
        max_score = float(assessment_subject.max_score)

        return BulkImportContext(
            assessment_subject=assessment_subject,
            enrollments_by_id=enrollments_by_id,
            existing_by_enrollment_id=existing_by_enrollment_id,
            max_score=max_score,
        )

    @staticmethod
    def _validate_item(*, item: dict, ctx: BulkImportContext) -> None:
        # Required fields
        if "enrollment_id" not in item:
            raise ValidationException(message="Missing enrollment_id")

        enrollment_id = item["enrollment_id"]
        if enrollment_id not in ctx.enrollments_by_id:
            raise ValidationException(
                message="Enrollment not in classroom for this assessment",
                field_errors={"enrollment_id": ["not_in_classroom"]},
            )

        is_absent = bool(item.get("is_absent", False))
        raw_score = item.get("raw_score", None)

        if is_absent:
            if raw_score is not None:
                raise ValidationException(
                    message="Absent student must not have a score",
                    field_errors={"raw_score": ["must_be_null_when_absent"]},
                )
        else:
            if raw_score is None:
                raise ValidationException(
                    message="Score is required when not absent",
                    field_errors={"raw_score": ["required_when_present"]},
                )
            try:
                score_val = float(raw_score)
            except (TypeError, ValueError):
                raise ValidationException(message="Invalid score value")
            if score_val < 0:
                raise ValidationException(message="Score cannot be negative")
            if score_val > ctx.max_score:
                raise ValidationException(
                    message=f"Score cannot exceed maximum score ({ctx.max_score})."
                )

    @staticmethod
    def preview_bulk_import(*, assessment_subject_id: int, grades: List[dict]) -> dict:
        ctx = StudentAssessmentService._get_bulk_import_context(
            assessment_subject_id=assessment_subject_id
        )

        def _extract_code(item: dict, exc: ValidationException) -> str:
            # Try to infer a machine-readable error code from field_errors/message
            fe = getattr(exc, "field_errors", None) or {}
            if "enrollment_id" in fe and "not_in_classroom" in fe.get("enrollment_id", []):
                return "not_in_classroom"
            if "raw_score" in fe and "must_be_null_when_absent" in fe.get("raw_score", []):
                return "absent_with_score"
            if "raw_score" in fe and "required_when_present" in fe.get("raw_score", []):
                return "score_required_when_present"
            msg = (getattr(exc, "message", None) or str(exc) or "").lower()
            if "missing enrollment_id" in msg:
                return "missing_enrollment_id"
            if "invalid score" in msg:
                return "invalid_score"
            if "cannot exceed maximum" in msg or "exceed maximum" in msg:
                return "score_exceeds_max"
            if "cannot be negative" in msg:
                return "negative_score"
            return "validation_error"

        creates, updates, errors = 0, 0, []
        for i, item in enumerate(grades):
            try:
                StudentAssessmentService._validate_item(item=item, ctx=ctx)
            except ValidationException as e:
                errors.append({
                    "index": i,
                    "enrollment_id": item.get("enrollment_id"),
                    "code": _extract_code(item, e),
                    "detail": str(e),
                })
                continue

            enrollment_id = item["enrollment_id"]
            if enrollment_id in ctx.existing_by_enrollment_id:
                updates += 1
            else:
                creates += 1

        return {
            "assessment_subject_id": assessment_subject_id,
            "max_score": ctx.max_score,
            "total": len(grades),
            "creates": creates,
            "updates": updates,
            "errors": errors,
        }

    @staticmethod
    @transaction.atomic
    def commit_bulk_import(*, assessment_subject_id: int, grades: List[dict], user=None) -> dict:
        ctx = StudentAssessmentService._get_bulk_import_context(
            assessment_subject_id=assessment_subject_id
        )

        to_create: List[StudentAssessment] = []
        to_update: List[StudentAssessment] = []

        # Strict validation (all-or-nothing) with structured aggregation of first error
        first_error: dict | None = None
        for idx, item in enumerate(grades):
            try:
                StudentAssessmentService._validate_item(item=item, ctx=ctx)
            except ValidationException as e:
                # mirror preview coding for commit error response
                code = "validation_error"
                fe = getattr(e, "field_errors", None) or {}
                if "enrollment_id" in fe and "not_in_classroom" in fe.get("enrollment_id", []):
                    code = "not_in_classroom"
                elif "raw_score" in fe and "must_be_null_when_absent" in fe.get("raw_score", []):
                    code = "absent_with_score"
                elif "raw_score" in fe and "required_when_present" in fe.get("raw_score", []):
                    code = "score_required_when_present"
                msg = (getattr(e, "message", None) or str(e) or "").lower()
                if code == "validation_error":
                    if "missing enrollment_id" in msg:
                        code = "missing_enrollment_id"
                    elif "invalid score" in msg:
                        code = "invalid_score"
                    elif "cannot exceed maximum" in msg or "exceed maximum" in msg:
                        code = "score_exceeds_max"
                    elif "cannot be negative" in msg:
                        code = "negative_score"
                first_error = {
                    "index": idx,
                    "enrollment_id": item.get("enrollment_id"),
                    "code": code,
                    "detail": str(e),
                }
                break

        if first_error:
            # raise ValidationException with structured details so DRF can render JSON consistently
            raise ValidationException(
                message="Bulk commit validation failed.",
                code=first_error["code"],
                details={"error": first_error},
            )

        for item in grades:
            enrollment_id = item["enrollment_id"]
            raw_score = item.get("raw_score")
            is_absent = bool(item.get("is_absent", False))
            is_excused = bool(item.get("is_excused", False))
            remark = item.get("remark", "")

            existing = ctx.existing_by_enrollment_id.get(enrollment_id)
            if existing:
                # Update existing
                existing.raw_score = None if is_absent else raw_score
                existing.is_absent = is_absent
                existing.is_excused = is_excused
                existing.remark = remark
                existing.updated_by = user
                to_update.append(existing)
            else:
                # Create new
                sa = StudentAssessment(
                    assessment_subject=ctx.assessment_subject,
                    student_enrollment_id=enrollment_id,
                    raw_score=None if is_absent else raw_score,
                    is_absent=is_absent,
                    is_excused=is_excused,
                    remark=remark,
                    created_by=user,
                    updated_by=user,
                )
                to_create.append(sa)

        created_count = 0
        updated_count = 0
        if to_create:
            StudentAssessment.objects.bulk_create(to_create, batch_size=500)
            created_count = len(to_create)
        if to_update:
            StudentAssessment.objects.bulk_update(
                to_update, ["raw_score", "is_absent", "is_excused", "remark", "updated_by", "updated_at"], batch_size=500
            )
            updated_count = len(to_update)

        return {
            "assessment_subject_id": assessment_subject_id,
            "created": created_count,
            "updated": updated_count,
            "total": len(grades),
        }
