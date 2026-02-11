from django.db.models import QuerySet

from domain.school_operations.models import SchoolYearLevelSubject


class SchoolYearLevelSubjectSelector:
    @staticmethod
    def list(*, school_year_level_id: int | None = None) -> QuerySet[SchoolYearLevelSubject]:
        qs = SchoolYearLevelSubject.objects.select_related("school_year_level", "subject")
        if school_year_level_id:
            qs = qs.filter(school_year_level_id=school_year_level_id)
        return qs

    @staticmethod
    def get(*, obj_id: int) -> SchoolYearLevelSubject:
        return SchoolYearLevelSubject.objects.select_related("school_year_level", "subject").get(id=obj_id)
