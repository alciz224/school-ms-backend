from django.db.models import QuerySet
from domain.enrollment.models import StudentEnrollment


class SchoolAdminStudentSelector:
    @staticmethod
    def list(*, search: str = None, academic_year: str = None, cycle: str = None, level: str = None, class_name: str = None, status: str = None, gender: str = None) -> QuerySet[StudentEnrollment]:
        """
        List student enrollments for the school admin portal, matching frontend `StudentsFilter`.
        """
        qs = StudentEnrollment.objects.filter(is_deleted=False).select_related(
            "student",
            "classroom",
            "previous_classroom",
            "school_year_level",
            "school_year_level__school_year_cycle",
            "school_year_level__school_year_cycle__school_year",
            "school_year_level__school_year_cycle__cycle",
            "school_year_level__track",
            "school_year_level__level",
        )

        if search:
            qs = qs.filter(first_name__icontains=search) | qs.filter(last_name__icontains=search) | qs.filter(annual_identifier__icontains=search)
            
        if academic_year:
            qs = qs.filter(school_year_level__school_year_cycle__school_year__name=academic_year)
            
        if cycle:
            qs = qs.filter(school_year_level__school_year_cycle__cycle__name=cycle)
            
        if level:
            qs = qs.filter(school_year_level__level__name=level)
            
        if class_name:
            qs = qs.filter(classroom__name=class_name)
            
        if status:
            qs = qs.filter(enrollment_status=status)
            
        # We don't have gender natively right now, so we can't filter on it easily,
        # but if we did, it would be qs.filter(student__gender=gender)
            
        return qs.order_by("-enrollment_date")
