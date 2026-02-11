"""Selectors for roster / portal-oriented queries."""

from django.db.models import Count, F, Q, QuerySet

from domain.enrollment.models import Classroom, StudentEnrollment


class RosterSelector:
    @staticmethod
    def get_classroom_roster(*, classroom_id: int) -> QuerySet[StudentEnrollment]:
        """Get active enrollments for a classroom, ordered by display_name logic."""
        return (
            StudentEnrollment.objects.filter(classroom_id=classroom_id, is_deleted=False)
            .exclude(enrollment_status="DROPPED")
            .select_related("student", "school_year_level")
            .order_by("last_name", "first_name", "classroom_suffix")
        )

    @staticmethod
    def get_school_year_level_enrollments(*, school_year_level_id: int) -> QuerySet[StudentEnrollment]:
        """Get all enrollments for a school year level."""
        return (
            StudentEnrollment.objects.filter(school_year_level_id=school_year_level_id, is_deleted=False)
            .select_related("student", "classroom", "school_year_level")
            .order_by("classroom__name", "last_name", "first_name", "classroom_suffix")
        )

    @staticmethod
    def get_classroom_with_stats(*, classroom_id: int) -> Classroom:
        """Get classroom annotated with student count and capacity remaining."""
        return (
            Classroom.objects.filter(id=classroom_id)
            .annotate(
                student_count=Count(
                    "student_enrollments",
                    filter=Q(student_enrollments__is_deleted=False)
                    & ~Q(student_enrollments__enrollment_status="DROPPED"),
                ),
                capacity_remaining=F("capacity") - Count(
                    "student_enrollments",
                    filter=Q(student_enrollments__is_deleted=False)
                    & ~Q(student_enrollments__enrollment_status="DROPPED"),
                ),
            )
            .first()
        )

    @staticmethod
    def get_student_enrollments(*, student_id: int) -> QuerySet[StudentEnrollment]:
        """Get enrollments for a specific student (for student portal)."""
        return (
            StudentEnrollment.objects.filter(student_id=student_id, is_deleted=False)
            .select_related("classroom", "school_year_level")
            .order_by("-enrollment_date")
        )
