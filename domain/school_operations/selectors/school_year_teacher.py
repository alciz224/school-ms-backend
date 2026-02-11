from django.db.models import QuerySet

from domain.school_operations.models import SchoolYearTeacher


class SchoolYearTeacherSelector:
    @staticmethod
    def list(*, school_year_id: int | None = None, status: str | None = None) -> QuerySet[SchoolYearTeacher]:
        qs = SchoolYearTeacher.objects.select_related("school_year", "teacher")
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        if status:
            qs = qs.filter(status=status)
        return qs

    @staticmethod
    def get(*, obj_id: int) -> SchoolYearTeacher:
        return SchoolYearTeacher.objects.select_related("school_year", "teacher").get(id=obj_id)

    @staticmethod
    def get_active_teachers(*, school_year_id: int) -> QuerySet[SchoolYearTeacher]:
        """Get all active teachers for a school year."""
        return SchoolYearTeacher.objects.filter(
            school_year_id=school_year_id, status="ACTIVE", is_deleted=False
        ).select_related("teacher")
