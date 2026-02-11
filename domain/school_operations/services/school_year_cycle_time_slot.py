from datetime import time

from domain.school_operations.constants import TimeSlotStatus
from domain.school_operations.models import SchoolYearCycleTimeSlot


class SchoolYearCycleTimeSlotService:
    @staticmethod
    def create(
        *,
        school_year_cycle,
        name: str,
        start_time: time,
        end_time: time,
        order: int = 1,
        status: str = TimeSlotStatus.ACTIVE,
        user=None,
    ) -> SchoolYearCycleTimeSlot:
        obj = SchoolYearCycleTimeSlot(
            school_year_cycle=school_year_cycle,
            name=name,
            start_time=start_time,
            end_time=end_time,
            order=order,
            status=status,
        )
        obj.save_by(user=user)
        return obj

    @staticmethod
    def update(
        *,
        obj: SchoolYearCycleTimeSlot,
        name: str | None = None,
        start_time: time | None = None,
        end_time: time | None = None,
        order: int | None = None,
        status: str | None = None,
        user=None,
    ) -> SchoolYearCycleTimeSlot:
        if name is not None:
            obj.name = name
        if start_time is not None:
            obj.start_time = start_time
        if end_time is not None:
            obj.end_time = end_time
        if order is not None:
            obj.order = order
        if status is not None:
            obj.status = status
        obj.save_by(user=user)
        return obj

    @staticmethod
    def delete(*, obj: SchoolYearCycleTimeSlot, user=None) -> SchoolYearCycleTimeSlot:
        obj.soft_delete(user=user)
        return obj
