from datetime import date

from domain.school_operations.models import SchoolYearCycleTerm


class SchoolYearCycleTermService:
    @staticmethod
    def create(*, school_year_cycle, term, start_date: date, end_date: date, user=None) -> SchoolYearCycleTerm:
        obj = SchoolYearCycleTerm(
            school_year_cycle=school_year_cycle,
            term=term,
            start_date=start_date,
            end_date=end_date,
        )
        obj.save_by(user=user)
        return obj

    @staticmethod
    def update(
        *, obj: SchoolYearCycleTerm, start_date: date | None = None, end_date: date | None = None, user=None
    ) -> SchoolYearCycleTerm:
        if start_date is not None:
            obj.start_date = start_date
        if end_date is not None:
            obj.end_date = end_date
        obj.save_by(user=user)
        return obj

    @staticmethod
    def delete(*, obj: SchoolYearCycleTerm, user=None) -> SchoolYearCycleTerm:
        obj.soft_delete(user=user)
        return obj
