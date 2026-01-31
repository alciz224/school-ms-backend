"""
SchoolYear selectors.

Query operations for SchoolYear model.
"""

from typing import Optional
from django.db.models import QuerySet, Q, Count, F

from domain.school_operations.models import School, SchoolYear
from domain.school_operations.constants import SchoolYearStatus
from domain.academic.models import AcademicYear


class SchoolYearSelector:
    """Selectors for querying SchoolYear data."""

    @staticmethod
    def get_by_id(school_year_id: int) -> Optional[SchoolYear]:
        """
        Get school year by ID.
        
        Args:
            school_year_id: SchoolYear ID
            
        Returns:
            SchoolYear instance or None
        """
        try:
            return SchoolYear.objects.get(id=school_year_id)
        except SchoolYear.DoesNotExist:
            return None

    @staticmethod
    def get_by_code(code: str) -> Optional[SchoolYear]:
        """
        Get school year by code.
        
        Args:
            code: SchoolYear code
            
        Returns:
            SchoolYear instance or None
        """
        try:
            return SchoolYear.objects.get(code=code)
        except SchoolYear.DoesNotExist:
            return None

    @staticmethod
    def get_current_for_school(school: School) -> Optional[SchoolYear]:
        """
        Get current school year for a school.
        
        Args:
            school: School instance
            
        Returns:
            SchoolYear instance or None
        """
        return SchoolYear.objects.get_current_for_school(school)

    @staticmethod
    def get_active_for_school(school: School) -> Optional[SchoolYear]:
        """
        Get active school year for a school.
        
        Args:
            school: School instance
            
        Returns:
            SchoolYear instance or None
        """
        return SchoolYear.objects.get_active_for_school(school)

    @staticmethod
    def list_by_school(
        school: School,
        status: Optional[str] = None,
        include_archived: bool = False
    ) -> QuerySet:
        """
        List school years for a specific school.
        
        Args:
            school: School instance
            status: Filter by status (optional)
            include_archived: Include archived years (default: False)
            
        Returns:
            QuerySet of SchoolYear instances
        """
        qs = SchoolYear.objects.filter(school=school)
        
        if status:
            qs = qs.filter(status=status)
        
        if not include_archived:
            qs = qs.exclude(status=SchoolYearStatus.ARCHIVED)
        
        return qs.select_related('school', 'academic_year')

    @staticmethod
    def list_by_academic_year(
        academic_year: AcademicYear,
        status: Optional[str] = None
    ) -> QuerySet:
        """
        List school years for a specific academic year.
        
        Args:
            academic_year: AcademicYear instance
            status: Filter by status (optional)
            
        Returns:
            QuerySet of SchoolYear instances
        """
        qs = SchoolYear.objects.filter(academic_year=academic_year)
        
        if status:
            qs = qs.filter(status=status)
        
        return qs.select_related('school', 'academic_year')

    @staticmethod
    def list_active() -> QuerySet:
        """
        List all active school years.
        
        Returns:
            QuerySet of active SchoolYear instances
        """
        return (
            SchoolYear.objects.get_active()
            .select_related('school', 'academic_year')
        )

    @staticmethod
    def list_planning() -> QuerySet:
        """
        List all school years in planning status.
        
        Returns:
            QuerySet of planning SchoolYear instances
        """
        return (
            SchoolYear.objects.get_planning()
            .select_related('school', 'academic_year')
        )

    @staticmethod
    def list_with_open_enrollment() -> QuerySet:
        """
        List school years with open enrollment.
        
        Returns:
            QuerySet of SchoolYear instances with open enrollment
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        return (
            SchoolYear.objects.filter(
                enrollment_start_date__lte=today,
                enrollment_end_date__gte=today,
                status__in=[SchoolYearStatus.PLANNING, SchoolYearStatus.ACTIVE]
            )
            .select_related('school', 'academic_year')
        )

    @staticmethod
    def list_with_available_capacity() -> QuerySet:
        """
        List school years with available capacity.
        
        Returns:
            QuerySet of SchoolYear instances with capacity
        """
        return (
            SchoolYear.objects.filter(
                Q(capacity__isnull=True) | 
                Q(current_enrollment_count__lt=F('capacity'))
            )
            .exclude(status=SchoolYearStatus.ARCHIVED)
            .select_related('school', 'academic_year')
        )

    @staticmethod
    def search(
        query: str,
        school: Optional[School] = None,
        academic_year: Optional[AcademicYear] = None,
        status: Optional[str] = None
    ) -> QuerySet:
        """
        Search school years by name, code, or description.
        
        Args:
            query: Search query
            school: Filter by school (optional)
            academic_year: Filter by academic year (optional)
            status: Filter by status (optional)
            
        Returns:
            QuerySet of matching SchoolYear instances
        """
        qs = SchoolYear.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query)
        )
        
        if school:
            qs = qs.filter(school=school)
        
        if academic_year:
            qs = qs.filter(academic_year=academic_year)
        
        if status:
            qs = qs.filter(status=status)
        
        return qs.select_related('school', 'academic_year')

    @staticmethod
    def get_statistics_by_academic_year(academic_year: AcademicYear) -> dict:
        """
        Get statistics for school years in an academic year.
        
        Args:
            academic_year: AcademicYear instance
            
        Returns:
            dict: Statistics
        """
        school_years = SchoolYear.objects.filter(academic_year=academic_year)
        
        stats = {
            'total_school_years': school_years.count(),
            'by_status': {
                'planning': school_years.filter(status=SchoolYearStatus.PLANNING).count(),
                'active': school_years.filter(status=SchoolYearStatus.ACTIVE).count(),
                'completed': school_years.filter(status=SchoolYearStatus.COMPLETED).count(),
                'archived': school_years.filter(status=SchoolYearStatus.ARCHIVED).count(),
            },
            'total_capacity': school_years.aggregate(
                total=Count('capacity')
            )['total'] or 0,
            'total_enrollment': school_years.aggregate(
                total=Count('current_enrollment_count')
            )['total'] or 0,
        }
        
        return stats

    @staticmethod
    def get_school_year_for_enrollment(
        school: School,
        academic_year: Optional[AcademicYear] = None
    ) -> Optional[SchoolYear]:
        """
        Get the appropriate school year for new enrollments.
        
        Prioritizes:
        1. Current year with open enrollment
        2. Active year with capacity
        3. Planning year with open enrollment
        
        Args:
            school: School instance
            academic_year: Filter by academic year (optional)
            
        Returns:
            SchoolYear instance or None
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        qs = SchoolYear.objects.filter(school=school)
        
        if academic_year:
            qs = qs.filter(academic_year=academic_year)
        
        # Try current year with open enrollment
        school_year = qs.filter(
            is_current=True,
            enrollment_start_date__lte=today,
            enrollment_end_date__gte=today
        ).first()
        
        if school_year and school_year.has_capacity():
            return school_year
        
        # Try active year with capacity
        school_year = qs.filter(
            status=SchoolYearStatus.ACTIVE
        ).first()
        
        if school_year and school_year.has_capacity():
            return school_year
        
        # Try planning year with open enrollment
        school_year = qs.filter(
            status=SchoolYearStatus.PLANNING,
            enrollment_start_date__lte=today,
            enrollment_end_date__gte=today
        ).first()
        
        if school_year and school_year.has_capacity():
            return school_year
        
        return None

    @staticmethod
    def list_overlapping_years(
        school: School,
        start_date,
        end_date,
        exclude_id: Optional[int] = None
    ) -> QuerySet:
        """
        Find school years with overlapping date ranges.
        
        Args:
            school: School instance
            start_date: Start date to check
            end_date: End date to check
            exclude_id: Exclude specific school year ID (optional)
            
        Returns:
            QuerySet of overlapping SchoolYear instances
        """
        qs = SchoolYear.objects.filter(
            school=school
        ).filter(
            Q(start_date__lte=end_date, end_date__gte=start_date)
        )
        
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        
        return qs

    @staticmethod
    def get_by_school_and_academic_year(
        school: School,
        academic_year: AcademicYear
    ) -> Optional[SchoolYear]:
        """
        Get school year by school and academic year combination.
        
        Args:
            school: School instance
            academic_year: AcademicYear instance
            
        Returns:
            SchoolYear instance or None
        """
        try:
            return SchoolYear.objects.get(
                school=school,
                academic_year=academic_year
            )
        except SchoolYear.DoesNotExist:
            return None

    @staticmethod
    def list_requiring_attention() -> QuerySet:
        """
        List school years requiring attention (low capacity, dates issues, etc.).
        
        Returns:
            QuerySet of SchoolYear instances
        """
        from django.utils import timezone
        today = timezone.now().date()
        
        # School years that are active but enrollment is still open past start date
        # or have reached 90% capacity, or end date is approaching
        return (
            SchoolYear.objects.filter(
                Q(
                    status=SchoolYearStatus.ACTIVE,
                    enrollment_end_date__gte=today,
                    start_date__lt=today
                ) |
                Q(
                    current_enrollment_count__gte=F('capacity') * 0.9,
                    capacity__isnull=False
                ) |
                Q(
                    status=SchoolYearStatus.ACTIVE,
                    end_date__lte=today
                )
            )
            .select_related('school', 'academic_year')
        )
