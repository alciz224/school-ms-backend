from django.db.models import QuerySet

from domain.school_operations.models import SchoolYearCycleTimeSlot


class SchoolYearCycleTimeSlotSelector:
    @staticmethod
    def list(*, school_year_cycle_id: int | None = None, status: str | None = None) -> QuerySet[SchoolYearCycleTimeSlot]:
        qs = SchoolYearCycleTimeSlot.objects.select_related("school_year_cycle")
        if school_year_cycle_id:
            qs = qs.filter(school_year_cycle_id=school_year_cycle_id)
        if status:
            qs = qs.filter(status=status)
        return qs.order_by("order", "start_time")

    @staticmethod
    def get(*, obj_id: int) -> SchoolYearCycleTimeSlot:
        return SchoolYearCycleTimeSlot.objects.select_related("school_year_cycle").get(id=obj_id)
