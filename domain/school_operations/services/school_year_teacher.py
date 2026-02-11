from datetime import date

from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import SchoolYearTeacher


class SchoolYearTeacherService:
    @staticmethod
    def create(
        *,
        school_year,
        teacher,
        status: str = SchoolYearTeacherStatus.ACTIVE,
        hire_date: date | None = None,
        end_date: date | None = None,
        user=None,
    ) -> SchoolYearTeacher:
        obj = SchoolYearTeacher(
            school_year=school_year,
            teacher=teacher,
            status=status,
            hire_date=hire_date,
            end_date=end_date,
        )
        obj.save_by(user=user)
        return obj

    @staticmethod
    def update(
        *,
        obj: SchoolYearTeacher,
        status: str | None = None,
        hire_date: date | None = None,
        end_date: date | None = None,
        user=None,
    ) -> SchoolYearTeacher:
        if status is not None:
            obj.status = status
        if hire_date is not None:
            obj.hire_date = hire_date
        if end_date is not None:
            obj.end_date = end_date
        obj.save_by(user=user)
        return obj

    @staticmethod
    def suspend(*, obj: SchoolYearTeacher, user=None) -> SchoolYearTeacher:
        obj.status = SchoolYearTeacherStatus.SUSPENDED
        obj.save_by(user=user)
        return obj

    @staticmethod
    def reactivate(*, obj: SchoolYearTeacher, user=None) -> SchoolYearTeacher:
        obj.status = SchoolYearTeacherStatus.ACTIVE
        obj.save_by(user=user)
        return obj

    @staticmethod
    def mark_left(*, obj: SchoolYearTeacher, end_date: date, user=None) -> SchoolYearTeacher:
        obj.status = SchoolYearTeacherStatus.LEFT
        obj.end_date = end_date
        obj.save_by(user=user)
        return obj

    @staticmethod
    def delete(*, obj: SchoolYearTeacher, user=None) -> SchoolYearTeacher:
        obj.soft_delete(user=user)
        return obj
