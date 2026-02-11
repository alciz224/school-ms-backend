from django.db.models import QuerySet

from domain.enrollment.models import StudentEnrollment


class StudentEnrollmentSelector:
    @staticmethod
    def list(*, school_year_level_id: int | None = None, classroom_id: int | None = None) -> QuerySet[StudentEnrollment]:
        qs = StudentEnrollment.objects.select_related("student", "school_year_level", "classroom")
        if school_year_level_id:
            qs = qs.filter(school_year_level_id=school_year_level_id)
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        return qs

    @staticmethod
    def get(*, enrollment_id: int) -> StudentEnrollment:
        return StudentEnrollment.objects.select_related("student", "school_year_level", "classroom").get(id=enrollment_id)
