from domain.enrollment.models import Classroom


class ClassroomService:
    @staticmethod
    def create(*, school_year_level, name: str, capacity=None, room_number=None, user=None) -> Classroom:
        obj = Classroom(
            school_year_level=school_year_level,
            name=name,
            capacity=capacity,
            room_number=room_number,
        )
        obj.save_by(user=user)
        return obj

    @staticmethod
    def update(*, obj: Classroom, name: str | None = None, capacity=None, room_number=None, user=None) -> Classroom:
        if name is not None:
            obj.name = name
        if capacity is not None:
            obj.capacity = capacity
        if room_number is not None:
            obj.room_number = room_number
        obj.save_by(user=user)
        return obj

    @staticmethod
    def delete(*, obj: Classroom, user=None) -> Classroom:
        # NOTE: dependency checks (student enrollments etc.) can be added later.
        obj.soft_delete(user=user)
        return obj
