"""Optimized selectors for assessment grading and reporting."""

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Dict, Iterable, List

from django.db.models import Avg, Count, F, Prefetch, Q, QuerySet

from domain.assessment.models import Assessment, AssessmentSubject, StudentAssessment
from domain.enrollment.models import StudentEnrollment


@dataclass(frozen=True)
class ClassroomGradingRow:
    enrollment_id: int
    display_name: str
    student_id: int | None
    existing_score: Decimal | None
    is_absent: bool
    is_excused: bool
    remark: str


class ClassroomGradingSelector:
    @staticmethod
    def get_classroom_grading_sheet(*, assessment_subject_id: int) -> Dict[str, Any]:
        """
        Return grading data for a classroom for the given assessment subject in ~2-3 queries.
        - Includes roster with existing scores and display names
        - Includes max_score and basic assessment subject meta
        """
        assessment_subject = (
            AssessmentSubject.objects.select_related(
                "assessment",
                "classroom",
                "school_year_level_subject__subject",
                "teacher_assignment__school_year_teacher__teacher",
            )
            
            .get(id=assessment_subject_id)
        )

        # Prefetch student assessments for this subject
        assessments_qs = (
            StudentAssessment.objects.filter(
                assessment_subject_id=assessment_subject_id, is_deleted=False
            )
            .only(
                "id",
                "student_enrollment_id",
                "raw_score",
                "is_absent",
                "is_excused",
                "remark",
            )
            .order_by("id")
        )

        enrollments = (
            StudentEnrollment.objects.filter(
                classroom_id=assessment_subject.classroom_id, is_deleted=False
            )
            .select_related("student", "classroom")
            .prefetch_related(Prefetch("student_assessments", queryset=assessments_qs))
            
            .order_by("last_name", "first_name", "classroom_suffix")
        )

        rows: List[ClassroomGradingRow] = []
        for e in enrollments:
            # there should be at most 1 for this subject/enrollment due to unique constraint
            if hasattr(e, "student_assessments"):
                assess_list = list(e.student_assessments.all())
            else:
                assess_list = []
            sa = assess_list[0] if assess_list else None
            rows.append(
                ClassroomGradingRow(
                    enrollment_id=e.id,
                    display_name=getattr(e, "display_name", f"{e.first_name} {e.last_name}"),
                    student_id=e.student_id if hasattr(e, "student_id") else None,
                    existing_score=getattr(sa, "raw_score", None) if sa else None,
                    is_absent=getattr(sa, "is_absent", False) if sa else False,
                    is_excused=getattr(sa, "is_excused", False) if sa else False,
                    remark=getattr(sa, "remark", "") if sa else "",
                )
            )

        return {
            "assessment_subject_id": assessment_subject.id,
            "subject_name": assessment_subject.school_year_level_subject.subject.name,
            "classroom_id": assessment_subject.classroom_id,
            "max_score": assessment_subject.max_score,
            "status": assessment_subject.status,
            "rows": [r.__dict__ for r in rows],
        }


class AssessmentOverviewSelector:
    @staticmethod
    def get_assessment_overview(*, assessment_id: int) -> Dict[str, Any]:
        """Return summary of assessment with subjects count and status breakdown."""
        a = (
            Assessment.objects.select_related("school_year", "school_year_cycle", "school_year_cycle_term")
            .only("id", "name", "status", "start_date", "end_date")
            .get(id=assessment_id)
        )

        subj_qs = AssessmentSubject.objects.filter(assessment_id=assessment_id, is_deleted=False)
        counts = subj_qs.values("status").annotate(c=Count("id"))
        status_counts = {row["status"]: row["c"] for row in counts}
        total_subjects = subj_qs.count()

        return {
            "assessment_id": a.id,
            "name": a.name,
            "status": a.status,
            "start_date": a.start_date,
            "end_date": a.end_date,
            "subjects_total": total_subjects,
            "subjects_by_status": status_counts,
        }


class StudentGradesSelector:
    @staticmethod
    def get_student_grades_history(*, student_enrollment_id: int) -> List[Dict[str, Any]]:
        """Return list of grades for a student enrollment across subjects (validated and draft)."""
        qs = (
            StudentAssessment.objects.filter(student_enrollment_id=student_enrollment_id, is_deleted=False)
            .select_related(
                "assessment_subject__assessment",
                "assessment_subject__school_year_level_subject__subject",
            )
            .only(
                "id",
                "raw_score",
                "is_absent",
                "is_excused",
                "status",
                "assessment_subject__max_score",
                "assessment_subject__assessment__name",
                "assessment_subject__school_year_level_subject__subject__name",
            )
            .order_by("assessment_subject__assessment__start_date")
        )

        results: List[Dict[str, Any]] = []
        for sa in qs:
            results.append(
                {
                    "student_assessment_id": sa.id,
                    "assessment_name": sa.assessment_subject.assessment.name,
                    "subject_name": sa.assessment_subject.school_year_level_subject.subject.name,
                    "raw_score": sa.raw_score,
                    "max_score": sa.assessment_subject.max_score,
                    "is_absent": sa.is_absent,
                    "is_excused": sa.is_excused,
                    "status": sa.status,
                }
            )
        return results

    @staticmethod
    def calculate_classroom_averages(*, classroom_id: int) -> Dict[str, Any]:
        """
        Compute per-subject averages for a given classroom using validated, non-absent grades.
        Returns: { subject_name: average_on_base, ... }
        """
        qs = (
            StudentAssessment.objects.filter(
                assessment_subject__classroom_id=classroom_id,
                status="VALIDATED",
                is_absent=False,
                is_deleted=False,
            )
            .select_related(
                "assessment_subject__school_year_level_subject__subject",
            )
            .values(
                "assessment_subject__school_year_level_subject__subject__name",
                "assessment_subject__max_score",
            )
            .annotate(avg_raw=Avg("raw_score"), cnt=Count("id"))
        )
        out: Dict[str, Any] = {}
        for row in qs:
            subj = row["assessment_subject__school_year_level_subject__subject__name"]
            max_score = row["assessment_subject__max_score"]
            avg_raw = row["avg_raw"] or 0
            # already same base across subjects; expose as-is
            out[subj] = {
                "average": avg_raw,
                "max_score": max_score,
                "count": row["cnt"],
            }
        return out
