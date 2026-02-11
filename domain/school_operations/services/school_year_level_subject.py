from decimal import Decimal

from domain.school_operations.models import SchoolYearLevelSubject


class SchoolYearLevelSubjectService:
    @staticmethod
    def create(*, school_year_level, subject, coefficient: Decimal, user=None) -> SchoolYearLevelSubject:
        obj = SchoolYearLevelSubject(
            school_year_level=school_year_level,
            subject=subject,
            coefficient=coefficient,
        )
        obj.save_by(user=user)
        return obj

    @staticmethod
    def update(*, obj: SchoolYearLevelSubject, coefficient: Decimal | None = None, user=None) -> SchoolYearLevelSubject:
        if coefficient is not None:
            obj.coefficient = coefficient
        obj.save_by(user=user)
        return obj

    @staticmethod
    def delete(*, obj: SchoolYearLevelSubject, user=None) -> SchoolYearLevelSubject:
        obj.soft_delete(user=user)
        return obj
