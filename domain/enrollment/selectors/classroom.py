from django.db.models import QuerySet

from domain.enrollment.models import Classroom


class ClassroomSelector:
    @staticmethod
    def list(*, school_year_level_id: int | None = None) -> QuerySet[Classroom]:
        qs = Classroom.objects.all()
        if school_year_level_id:
            qs = qs.filter(school_year_level_id=school_year_level_id)
        return qs

    @staticmethod
    def get(*, classroom_id: int) -> Classroom:
        return Classroom.objects.get(id=classroom_id)
