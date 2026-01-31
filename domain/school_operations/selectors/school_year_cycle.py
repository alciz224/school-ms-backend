"""SchoolYearCycle selector for read operations."""
from typing import Optional

from django.db.models import Prefetch, Q, QuerySet

from domain.school_operations.models.school_year_cycle import SchoolYearCycle


class SchoolYearCycleSelector:
    """
    Selector for querying SchoolYearCycle instances.

    Handles:
        - Retrieving cycle configurations
        - Filtering and searching
        - Optimized queries with prefetching
    """

    @staticmethod
    def get_queryset() -> QuerySet[SchoolYearCycle]:
        """
        Get base queryset for SchoolYearCycle.

        Returns:
            QuerySet: Base queryset with common select_related
        """
        return SchoolYearCycle.objects.select_related(
            "school_year",
            "school_year__school",
            "school_year__academic_year",
            "cycle",
            "term_type",
            "created_by",
            "updated_by",
        ).filter(is_deleted=False)

    @staticmethod
    def get_by_id(*, id: int) -> Optional[SchoolYearCycle]:
        """
        Get a school year cycle by ID.

        Args:
            id: SchoolYearCycle ID

        Returns:
            SchoolYearCycle or None
        """
        try:
            return SchoolYearCycleSelector.get_queryset().get(id=id)
        except SchoolYearCycle.DoesNotExist:
            return None

    @staticmethod
    def get_by_school_year_and_cycle(
        *, school_year_id: int, cycle_id: int
    ) -> Optional[SchoolYearCycle]:
        """
        Get a school year cycle by school_year and cycle (unique combination).

        Args:
            school_year_id: SchoolYear ID
            cycle_id: Cycle ID

        Returns:
            SchoolYearCycle or None
        """
        try:
            return SchoolYearCycleSelector.get_queryset().get(
                school_year_id=school_year_id, cycle_id=cycle_id
            )
        except SchoolYearCycle.DoesNotExist:
            return None

    @staticmethod
    def list_all() -> QuerySet[SchoolYearCycle]:
        """
        List all school year cycles.

        Returns:
            QuerySet: All non-deleted cycles
        """
        return SchoolYearCycleSelector.get_queryset()

    @staticmethod
    def list_by_school_year(*, school_year_id: int) -> QuerySet[SchoolYearCycle]:
        """
        List all cycles for a specific school year.

        Args:
            school_year_id: SchoolYear ID

        Returns:
            QuerySet: Cycles for the school year
        """
        return SchoolYearCycleSelector.get_queryset().filter(
            school_year_id=school_year_id
        )

    @staticmethod
    def list_by_school(*, school_id: int) -> QuerySet[SchoolYearCycle]:
        """
        List all cycles for a specific school across all years.

        Args:
            school_id: School ID

        Returns:
            QuerySet: Cycles for the school
        """
        return SchoolYearCycleSelector.get_queryset().filter(
            school_year__school_id=school_id
        )

    @staticmethod
    def list_by_cycle(*, cycle_id: int) -> QuerySet[SchoolYearCycle]:
        """
        List all school year configurations for a specific cycle.

        Args:
            cycle_id: Cycle ID

        Returns:
            QuerySet: School year cycles for the cycle
        """
        return SchoolYearCycleSelector.get_queryset().filter(cycle_id=cycle_id)

    @staticmethod
    def list_by_term_type(*, term_type_id: int) -> QuerySet[SchoolYearCycle]:
        """
        List all cycles using a specific term type.

        Args:
            term_type_id: TermType ID

        Returns:
            QuerySet: Cycles using the term type
        """
        return SchoolYearCycleSelector.get_queryset().filter(term_type_id=term_type_id)

    @staticmethod
    def list_active_cycles() -> QuerySet[SchoolYearCycle]:
        """
        List cycles for active school years.

        Returns:
            QuerySet: Cycles for currently active school years
        """
        from django.utils import timezone

        now = timezone.now().date()

        return SchoolYearCycleSelector.get_queryset().filter(
            school_year__start_date__lte=now,
            school_year__end_date__gte=now,
        )

    @staticmethod
    def list_by_school_and_active_year(*, school_id: int) -> QuerySet[SchoolYearCycle]:
        """
        List cycles for a school's active school year.

        Args:
            school_id: School ID

        Returns:
            QuerySet: Cycles for the school's active year
        """
        from django.utils import timezone

        now = timezone.now().date()

        return SchoolYearCycleSelector.get_queryset().filter(
            school_year__school_id=school_id,
            school_year__start_date__lte=now,
            school_year__end_date__gte=now,
        )

    @staticmethod
    def filter(
        *,
        school_year_id: Optional[int] = None,
        school_id: Optional[int] = None,
        cycle_id: Optional[int] = None,
        term_type_id: Optional[int] = None,
        academic_year_id: Optional[int] = None,
    ) -> QuerySet[SchoolYearCycle]:
        """
        Filter school year cycles by multiple criteria.

        Args:
            school_year_id: Filter by school year
            school_id: Filter by school
            cycle_id: Filter by cycle
            term_type_id: Filter by term type
            academic_year_id: Filter by academic year

        Returns:
            QuerySet: Filtered cycles
        """
        queryset = SchoolYearCycleSelector.get_queryset()

        if school_year_id is not None:
            queryset = queryset.filter(school_year_id=school_year_id)

        if school_id is not None:
            queryset = queryset.filter(school_year__school_id=school_id)

        if cycle_id is not None:
            queryset = queryset.filter(cycle_id=cycle_id)

        if term_type_id is not None:
            queryset = queryset.filter(term_type_id=term_type_id)

        if academic_year_id is not None:
            queryset = queryset.filter(school_year__academic_year_id=academic_year_id)

        return queryset

    @staticmethod
    def search(*, query: str) -> QuerySet[SchoolYearCycle]:
        """
        Search school year cycles by cycle name or school year.

        Args:
            query: Search string

        Returns:
            QuerySet: Matching cycles
        """
        return SchoolYearCycleSelector.get_queryset().filter(
            Q(cycle__name__icontains=query)
            | Q(cycle__code__icontains=query)
            | Q(school_year__school__name__icontains=query)
            | Q(term_type__name__icontains=query)
        )

    @staticmethod
    def exists(*, school_year_id: int, cycle_id: int) -> bool:
        """
        Check if a cycle configuration exists for a school year.

        Args:
            school_year_id: SchoolYear ID
            cycle_id: Cycle ID

        Returns:
            bool: True if exists, False otherwise
        """
        return SchoolYearCycleSelector.get_queryset().filter(
            school_year_id=school_year_id, cycle_id=cycle_id
        ).exists()

    @staticmethod
    def count_by_school_year(*, school_year_id: int) -> int:
        """
        Count cycles for a school year.

        Args:
            school_year_id: SchoolYear ID

        Returns:
            int: Number of cycles
        """
        return SchoolYearCycleSelector.list_by_school_year(
            school_year_id=school_year_id
        ).count()
