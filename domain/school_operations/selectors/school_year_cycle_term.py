from django.db.models import QuerySet

from domain.school_operations.models import SchoolYearCycleTerm


class SchoolYearCycleTermSelector:
    @staticmethod
    def list(*, school_year_cycle_id: int | None = None) -> QuerySet[SchoolYearCycleTerm]:
        qs = SchoolYearCycleTerm.objects.select_related("school_year_cycle", "term")
        if school_year_cycle_id:
            qs = qs.filter(school_year_cycle_id=school_year_cycle_id)
        return qs.order_by("term__order")

    @staticmethod
    def get(*, obj_id: int) -> SchoolYearCycleTerm:
        return SchoolYearCycleTerm.objects.select_related("school_year_cycle", "term").get(id=obj_id)
