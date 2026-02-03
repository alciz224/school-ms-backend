"""
AcademicYear selectors.
"""

from django.db.models import QuerySet, Q
from typing import Optional

from domain.academic.models import AcademicYear
from domain.academic.constants import AcademicYearStatus


class AcademicYearSelector:
    """Selector for academic year queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[AcademicYear]:
        """
        Get all academic years.

        Args:
            include_deleted: If True, include soft-deleted years

        Returns:
            QuerySet of academic years
        """
        if include_deleted:
            return AcademicYear.all_objects.all()
        return AcademicYear.objects.all()

    @staticmethod
    def get_by_id(*, year_id: int, include_deleted: bool = False) -> Optional[AcademicYear]:
        """
        Get an academic year by ID.

        Args:
            year_id: Academic year ID
            include_deleted: If True, include soft-deleted years

        Returns:
            AcademicYear instance or None
        """
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        return manager.filter(id=year_id).first()

    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[AcademicYear]:
        """
        Get an academic year by code.

        Args:
            code: Academic year code (e.g., "2024-2025")
            include_deleted: If True, include soft-deleted years

        Returns:
            AcademicYear instance or None
        """
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        return manager.filter(code__iexact=code.strip()).first()

    @staticmethod
    def get_current() -> Optional[AcademicYear]:
        """
        Get the current academic year.

        Returns:
            Current AcademicYear instance or None
        """
        return AcademicYear.objects.get_current()

    @staticmethod
    def get_active() -> QuerySet[AcademicYear]:
        """
        Get all active academic years.

        Returns:
            QuerySet of active academic years
        """
        return AcademicYear.objects.active()

    @staticmethod
    def get_by_status(*, status: str, include_deleted: bool = False) -> QuerySet[AcademicYear]:
        """
        Get academic years by status.

        Args:
            status: Academic year status
            include_deleted: If True, include soft-deleted years

        Returns:
            QuerySet of academic years with specified status
        """
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        return manager.filter(status=status)

    @staticmethod
    def get_draft() -> QuerySet[AcademicYear]:
        """
        Get all draft academic years.

        Returns:
            QuerySet of draft academic years
        """
        return AcademicYear.objects.filter(status=AcademicYearStatus.DRAFT)

    @staticmethod
    def get_archived() -> QuerySet[AcademicYear]:
        """
        Get all archived academic years.

        Returns:
            QuerySet of archived academic years
        """
        return AcademicYear.objects.filter(status=AcademicYearStatus.ARCHIVED)

    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[AcademicYear]:
        """
        Search academic years by code.

        Args:
            query: Search query
            include_deleted: If True, include soft-deleted years

        Returns:
            QuerySet of matching academic years
        """
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        return manager.filter(code__icontains=query)

    @staticmethod
    def get_by_year_range(*, start_year: int = None, end_year: int = None, 
                         include_deleted: bool = False) -> QuerySet[AcademicYear]:
        """
        Get academic years by year range.

        Args:
            start_year: Filter by start year
            end_year: Filter by end year  
            include_deleted: If True, include soft-deleted years

        Returns:
            QuerySet of academic years in specified range
        """
        manager = AcademicYear.all_objects if include_deleted else AcademicYear.objects
        queryset = manager.all()
        
        if start_year is not None:
            queryset = queryset.filter(start_year=start_year)
        if end_year is not None:
            queryset = queryset.filter(end_year=end_year)
            
        return queryset

    @staticmethod
    def get_overlapping_years(*, start_year: int, end_year: int,
                            exclude_id: int = None) -> QuerySet[AcademicYear]:
        """
        Get academic years that overlap with given period.

        Args:
            start_year: Period start year
            end_year: Period end year
            exclude_id: Exclude academic year with this ID

        Returns:
            QuerySet of overlapping academic years
        """
        queryset = AcademicYear.objects.filter(
            Q(start_year__lte=end_year) & Q(end_year__gte=start_year)
        )
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset

    @staticmethod
    def get_recent(*, limit: int = 5) -> QuerySet[AcademicYear]:
        """
        Get recent academic years ordered by start year descending.

        Args:
            limit: Number of years to return

        Returns:
            QuerySet of recent academic years
        """
        return AcademicYear.objects.order_by('-start_year')[:limit]

    @staticmethod
    def exists_by_period(*, start_year: int, end_year: int, 
                        exclude_id: int = None) -> bool:
        """
        Check if an academic year exists for the given period.

        Args:
            start_year: Period start year
            end_year: Period end year
            exclude_id: Exclude academic year with this ID

        Returns:
            True if academic year exists for the period
        """
        queryset = AcademicYear.objects.filter(
            start_year=start_year,
            end_year=end_year
        )
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
            
        return queryset.exists()

    @staticmethod
    def has_current_year() -> bool:
        """
        Check if there is a current academic year.

        Returns:
            True if current academic year exists
        """
        return AcademicYear.objects.filter(is_current=True).exists()