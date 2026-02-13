from typing import Dict, List

from domain.assessment.models import ReportCard, Transcript


class ReportCardSelector:
    @staticmethod
    def get_for_student_term(*, student_enrollment_id: int, term_id: int) -> ReportCard:
        return ReportCard.objects.select_related(
            "student_enrollment",
            "school_year_cycle_term",
            "classroom",
        ).prefetch_related("subjects").get(
            student_enrollment_id=student_enrollment_id,
            school_year_cycle_term_id=term_id,
            is_deleted=False,
        )

    @staticmethod
    def list_for_classroom_term(*, classroom_id: int, term_id: int):
        return ReportCard.objects.filter(
            classroom_id=classroom_id,
            school_year_cycle_term_id=term_id,
            is_deleted=False,
        ).select_related("student_enrollment").prefetch_related("subjects")


class TranscriptSelector:
    @staticmethod
    def get_for_student_year(*, student_enrollment_id: int, school_year_id: int) -> Transcript:
        return Transcript.objects.get(
            student_enrollment_id=student_enrollment_id,
            school_year_id=school_year_id,
            is_deleted=False,
        )
