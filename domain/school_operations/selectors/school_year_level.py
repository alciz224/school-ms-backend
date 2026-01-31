"""SchoolYearLevel selector for read operations."""
from typing import Optional

from django.db.models import Q, QuerySet

from domain.school_operations.models.school_year_level import SchoolYearLevel


class SchoolYearLevelSelector:
    """
    Selector for querying SchoolYearLevel instances.

    Handles:
        - Retrieving level configurations
        - Filtering and searching
        - Optimized queries with prefetching
    """

    @staticmethod
    def get_queryset() -> QuerySet[SchoolYearLevel]:
        """
        Get base queryset for SchoolYearLevel.

        Returns:
            QuerySet: Base queryset with common select_related
        """
        return SchoolYearLevel.objects.select_related(
            "school_year_cycle",
            "school_year_cycle__school_year",
            "school_year_cycle__school_year__school",
            "school_year_cycle__school_year__academic_year",
            "school_year_cycle__cycle",
            "school_year_cycle__term_type",
            "level",
            "level__cycle",
            "track",
            "track__cycle",
            "created_by",
            "updated_by",
        ).filter(is_deleted=False)

    @staticmethod
    def get_by_id(*, id: int) -> Optional[SchoolYearLevel]:
        """
        Get a school year level by ID.

        Args:
            id: SchoolYearLevel ID

        Returns:
            SchoolYearLevel or None
        """
        try:
            return SchoolYearLevelSelector.get_queryset().get(id=id)
        except SchoolYearLevel.DoesNotExist:
            return None

    @staticmethod
    def get_by_unique_fields(
        *, school_year_cycle_id: int, level_id: int, track_id: Optional[int] = None
    ) -> Optional[SchoolYearLevel]:
        """
        Get a school year level by its unique fields.

        Args:
            school_year_cycle_id: SchoolYearCycle ID
            level_id: Level ID
            track_id: Track ID (optional)

        Returns:
            SchoolYearLevel or None
        """
        try:
            return SchoolYearLevelSelector.get_queryset().get(
                school_year_cycle_id=school_year_cycle_id,
                level_id=level_id,
                track_id=track_id,
            )
        except SchoolYearLevel.DoesNotExist:
            return None

    @staticmethod
    def list_all() -> QuerySet[SchoolYearLevel]:
        """
        List all school year levels.

        Returns:
            QuerySet: All non-deleted levels
        """
        return SchoolYearLevelSelector.get_queryset()

    @staticmethod
    def list_by_school_year_cycle(
        *, school_year_cycle_id: int
    ) -> QuerySet[SchoolYearLevel]:
        """
        List all levels for a specific school year cycle.

        Args:
            school_year_cycle_id: SchoolYearCycle ID

        Returns:
            QuerySet: Levels for the school year cycle
        """
        return SchoolYearLevelSelector.get_queryset().filter(
            school_year_cycle_id=school_year_cycle_id
        )

    @staticmethod
    def list_by_school_year(*, school_year_id: int) -> QuerySet[SchoolYearLevel]:
        """
        List all levels for a specific school year.

        Args:
            school_year_id: SchoolYear ID

        Returns:
            QuerySet: Levels for the school year
        """
        return SchoolYearLevelSelector.get_queryset().filter(
            school_year_cycle__school_year_id=school_year_id
        )

    @staticmethod
    def list_by_school(*, school_id: int) -> QuerySet[SchoolYearLevel]:
        """
        List all levels for a specific school across all years.

        Args:
            school_id: School ID

        Returns:
            QuerySet: Levels for the school
        """
        return SchoolYearLevelSelector.get_queryset().filter(
            school_year_cycle__school_year__school_id=school_id
        )

    @staticmethod
    def list_by_level(*, level_id: int) -> QuerySet[SchoolYearLevel]:
        """
        List all school year configurations for a specific level.

        Args:
            level_id: Level ID

        Returns:
            QuerySet: School year levels for the level
        """
        return SchoolYearLevelSelector.get_queryset().filter(level_id=level_id)

    @staticmethod
    def list_by_track(*, track_id: int) -> QuerySet[SchoolYearLevel]:
        """
        List all levels using a specific track.

        Args:
            track_id: Track ID

        Returns:
            QuerySet: Levels using the track
        """
        return SchoolYearLevelSelector.get_queryset().filter(track_id=track_id)

    @staticmethod
    def list_by_cycle(*, cycle_id: int) -> QuerySet[SchoolYearLevel]:
        """
        List all levels for a specific cycle across all school years.

        Args:
            cycle_id: Cycle ID

        Returns:
            QuerySet: Levels for the cycle
        """
        return SchoolYearLevelSelector.get_queryset().filter(
            school_year_cycle__cycle_id=cycle_id
        )

    @staticmethod
    def list_active_levels() -> QuerySet[SchoolYearLevel]:
        """
        List levels for active school years.

        Returns:
            QuerySet: Levels for currently active school years
        """
        from django.utils import timezone

        now = timezone.now().date()

        return SchoolYearLevelSelector.get_queryset().filter(
            school_year_cycle__school_year__start_date__lte=now,
            school_year_cycle__school_year__end_date__gte=now,
        )

    @staticmethod
    def list_by_school_and_active_year(*, school_id: int) -> QuerySet[SchoolYearLevel]:
        """
        List levels for a school's active school year.

        Args:
            school_id: School ID

        Returns:
            QuerySet: Levels for the school's active year
        """
        from django.utils import timezone

        now = timezone.now().date()

        return SchoolYearLevelSelector.get_queryset().filter(
            school_year_cycle__school_year__school_id=school_id,
            school_year_cycle__school_year__start_date__lte=now,
            school_year_cycle__school_year__end_date__gte=now,
        )

    @staticmethod
    def filter(
        *,
        school_year_cycle_id: Optional[int] = None,
        school_year_id: Optional[int] = None,
        school_id: Optional[int] = None,
        cycle_id: Optional[int] = None,
        level_id: Optional[int] = None,
        track_id: Optional[int] = None,
        academic_year_id: Optional[int] = None,
    ) -> QuerySet[SchoolYearLevel]:
        """
        Filter school year levels by multiple criteria.

        Args:
            school_year_cycle_id: Filter by school year cycle
            school_year_id: Filter by school year
            school_id: Filter by school
            cycle_id: Filter by cycle
            level_id: Filter by level
            track_id: Filter by track
            academic_year_id: Filter by academic year

        Returns:
            QuerySet: Filtered levels
        """
        queryset = SchoolYearLevelSelector.get_queryset()

        if school_year_cycle_id is not None:
            queryset = queryset.filter(school_year_cycle_id=school_year_cycle_id)

        if school_year_id is not None:
            queryset = queryset.filter(
                school_year_cycle__school_year_id=school_year_id
            )

        if school_id is not None:
            queryset = queryset.filter(
                school_year_cycle__school_year__school_id=school_id
            )

        if cycle_id is not None:
            queryset = queryset.filter(school_year_cycle__cycle_id=cycle_id)

        if level_id is not None:
            queryset = queryset.filter(level_id=level_id)

        if track_id is not None:
            queryset = queryset.filter(track_id=track_id)

        if academic_year_id is not None:
            queryset = queryset.filter(
                school_year_cycle__school_year__academic_year_id=academic_year_id
            )

        return queryset

    @staticmethod
    def search(*, query: str) -> QuerySet[SchoolYearLevel]:
        """
        Search school year levels by level name or track name.

        Args:
            query: Search string

        Returns:
            QuerySet: Matching levels
        """
        return SchoolYearLevelSelector.get_queryset().filter(
            Q(level__name__icontains=query)
            | Q(level__code__icontains=query)
            | Q(track__name__icontains=query)
            | Q(track__code__icontains=query)
            | Q(school_year_cycle__school_year__school__name__icontains=query)
        )

    @staticmethod
    def exists(
        *, school_year_cycle_id: int, level_id: int, track_id: Optional[int] = None
    ) -> bool:
        """
        Check if a level configuration exists.

        Args:
            school_year_cycle_id: SchoolYearCycle ID
            level_id: Level ID
            track_id: Track ID (optional)

        Returns:
            bool: True if exists, False otherwise
        """
        return SchoolYearLevelSelector.get_queryset().filter(
            school_year_cycle_id=school_year_cycle_id,
            level_id=level_id,
            track_id=track_id,
        ).exists()

    @staticmethod
    def count_by_school_year_cycle(*, school_year_cycle_id: int) -> int:
        """
        Count levels for a school year cycle.

        Args:
            school_year_cycle_id: SchoolYearCycle ID

        Returns:
            int: Number of levels
        """
        return SchoolYearLevelSelector.list_by_school_year_cycle(
            school_year_cycle_id=school_year_cycle_id
        ).count()
