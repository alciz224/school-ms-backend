"""
School selectors.
"""

from django.db.models import QuerySet, Count, Q, Avg
from typing import Optional

from domain.school_operations.models import School
from domain.school_operations.constants import SchoolStatus, SchoolType, SchoolOwnership
from domain.geography.models import Locality, RegionAdministrative


class SchoolSelector:
    """Selector for school queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get all schools.

        Args:
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools
        """
        if include_deleted:
            return School.all_objects.all()
        return School.objects.all()

    @staticmethod
    def get_by_id(*, school_id: int, include_deleted: bool = False) -> Optional[School]:
        """
        Get a school by ID.

        Args:
            school_id: School ID
            include_deleted: If True, include soft-deleted schools

        Returns:
            School instance or None
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.filter(id=school_id).first()

    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Optional[School]:
        """
        Get a school by code.

        Args:
            code: School code (e.g., "LYC-FILIMA-001")
            include_deleted: If True, include soft-deleted schools

        Returns:
            School instance or None
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.filter(code__iexact=code.strip()).first()

    @staticmethod
    def get_active() -> QuerySet[School]:
        """
        Get all active schools.

        Returns:
            QuerySet of active schools
        """
        return School.objects.active()

    @staticmethod
    def get_by_status(*, status: str, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools by status.

        Args:
            status: School status
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools with specified status
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.filter(status=status)

    @staticmethod
    def get_draft() -> QuerySet[School]:
        """
        Get all draft schools.

        Returns:
            QuerySet of draft schools
        """
        return School.objects.filter(status=SchoolStatus.DRAFT)

    @staticmethod
    def get_suspended() -> QuerySet[School]:
        """
        Get all suspended schools.

        Returns:
            QuerySet of suspended schools
        """
        return School.objects.filter(status=SchoolStatus.SUSPENDED)

    @staticmethod
    def get_closed() -> QuerySet[School]:
        """
        Get all closed schools.

        Returns:
            QuerySet of closed schools
        """
        return School.objects.filter(status=SchoolStatus.CLOSED)

    @staticmethod
    def get_operational() -> QuerySet[School]:
        """
        Get all operational (active) schools.

        Returns:
            QuerySet of operational schools
        """
        return School.objects.active()

    @staticmethod
    def get_by_locality(*, locality: Locality, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools in a specific locality.

        Args:
            locality: Locality instance
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools in the locality
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.by_locality(locality)

    @staticmethod
    def get_by_region(*, region: RegionAdministrative, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools in a specific region.

        Args:
            region: Region instance
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools in the region
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.by_region(region)

    @staticmethod
    def get_by_type(*, school_type: str, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools of a specific type.

        Args:
            school_type: School type constant
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools of specified type
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.by_type(school_type)

    @staticmethod
    def get_by_ownership(*, ownership: str, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools by ownership type.

        Args:
            ownership: Ownership type constant
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools with specified ownership
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.filter(ownership=ownership)

    @staticmethod
    def get_public_schools(*, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get all public schools.

        Args:
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of public schools
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.public_schools()

    @staticmethod
    def get_private_schools(*, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get all private schools.

        Args:
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of private schools
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.private_schools()

    @staticmethod
    def get_by_capacity_range(*, min_capacity: int = None, max_capacity: int = None,
                             include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools within a capacity range.

        Args:
            min_capacity: Minimum capacity (inclusive)
            max_capacity: Maximum capacity (inclusive)
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools within capacity range
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.with_capacity(min_capacity, max_capacity)

    @staticmethod
    def get_with_staff() -> QuerySet[School]:
        """
        Get schools that have assigned staff (director or registrar).

        Returns:
            QuerySet of schools with staff
        """
        return School.objects.filter(
            Q(director__isnull=False) | Q(registrar__isnull=False),
            is_deleted=False
        )

    @staticmethod
    def get_without_staff() -> QuerySet[School]:
        """
        Get schools without assigned staff.

        Returns:
            QuerySet of schools without staff
        """
        return School.objects.filter(
            director__isnull=True,
            registrar__isnull=True,
            is_deleted=False
        )

    @staticmethod
    def get_by_director(*, director, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools managed by a specific director.

        Args:
            director: User instance
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools managed by director
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.filter(director=director)

    @staticmethod
    def get_by_registrar(*, registrar, include_deleted: bool = False) -> QuerySet[School]:
        """
        Get schools administered by a specific registrar.

        Args:
            registrar: User instance
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of schools administered by registrar
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.filter(registrar=registrar)

    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[School]:
        """
        Search schools by name, code, or address.

        Args:
            query: Search query
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of matching schools
        """
        manager = School.all_objects if include_deleted else School.objects
        return manager.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(address__icontains=query)
        )

    @staticmethod
    def filter_schools(*, locality: Locality = None, region: RegionAdministrative = None,
                      school_type: str = None, ownership: str = None,
                      status: str = None, min_capacity: int = None,
                      max_capacity: int = None, has_staff: bool = None,
                      include_deleted: bool = False) -> QuerySet[School]:
        """
        Filter schools by multiple criteria.

        Args:
            locality: Filter by locality
            region: Filter by region
            school_type: Filter by school type
            ownership: Filter by ownership type
            status: Filter by status
            min_capacity: Minimum capacity
            max_capacity: Maximum capacity
            has_staff: Filter schools with/without staff
            include_deleted: If True, include soft-deleted schools

        Returns:
            QuerySet of filtered schools
        """
        manager = School.all_objects if include_deleted else School.objects
        queryset = manager.all()

        if locality:
            queryset = queryset.filter(locality=locality)
        if region:
            queryset = queryset.filter(locality__administrative_unit__region=region)
        if school_type:
            queryset = queryset.filter(school_type=school_type)
        if ownership:
            queryset = queryset.filter(ownership=ownership)
        if status:
            queryset = queryset.filter(status=status)
        if min_capacity is not None:
            queryset = queryset.filter(capacity__gte=min_capacity)
        if max_capacity is not None:
            queryset = queryset.filter(capacity__lte=max_capacity)
        if has_staff is not None:
            if has_staff:
                queryset = queryset.filter(
                    Q(director__isnull=False) | Q(registrar__isnull=False)
                )
            else:
                queryset = queryset.filter(
                    director__isnull=True,
                    registrar__isnull=True
                )

        return queryset

    @staticmethod
    def get_statistics(*, locality: Locality = None, region: RegionAdministrative = None,
                      school_type: str = None) -> dict:
        """
        Get school statistics.

        Args:
            locality: Filter by locality
            region: Filter by region
            school_type: Filter by school type

        Returns:
            Dictionary containing statistics
        """
        queryset = School.objects.all()

        if locality:
            queryset = queryset.filter(locality=locality)
        if region:
            queryset = queryset.filter(locality__administrative_unit__region=region)
        if school_type:
            queryset = queryset.filter(school_type=school_type)

        stats = queryset.aggregate(
            total=Count('id'),
            active=Count('id', filter=Q(status=SchoolStatus.ACTIVE)),
            suspended=Count('id', filter=Q(status=SchoolStatus.SUSPENDED)),
            draft=Count('id', filter=Q(status=SchoolStatus.DRAFT)),
            closed=Count('id', filter=Q(status=SchoolStatus.CLOSED)),
            public=Count('id', filter=Q(ownership=SchoolOwnership.PUBLIC)),
            private=Count('id', filter=Q(ownership=SchoolOwnership.PRIVATE)),
            with_director=Count('id', filter=Q(director__isnull=False)),
            with_registrar=Count('id', filter=Q(registrar__isnull=False)),
            avg_capacity=Avg('capacity'),
        )

        return stats

    @staticmethod
    def get_by_type_statistics() -> dict:
        """
        Get school count by type.

        Returns:
            Dictionary with counts by school type
        """
        schools = School.objects.all()
        
        stats = {
            school_type[0]: schools.filter(school_type=school_type[0]).count()
            for school_type in SchoolType.CHOICES
        }
        
        return stats

    @staticmethod
    def get_by_region_statistics() -> QuerySet:
        """
        Get school counts by region.

        Returns:
            QuerySet with region annotations
        """
        from domain.geography.models import RegionAdministrative
        
        return RegionAdministrative.objects.annotate(
            total_schools=Count('administrative_units__localities__schools',
                              filter=Q(administrative_units__localities__schools__is_deleted=False)),
            active_schools=Count('administrative_units__localities__schools',
                                filter=Q(
                                    administrative_units__localities__schools__status=SchoolStatus.ACTIVE,
                                    administrative_units__localities__schools__is_deleted=False
                                ))
        )

    @staticmethod
    def get_capacity_statistics(*, locality: Locality = None,
                               region: RegionAdministrative = None) -> dict:
        """
        Get capacity-related statistics.

        Args:
            locality: Filter by locality
            region: Filter by region

        Returns:
            Dictionary containing capacity statistics
        """
        queryset = School.objects.filter(capacity__isnull=False)

        if locality:
            queryset = queryset.filter(locality=locality)
        if region:
            queryset = queryset.filter(locality__administrative_unit__region=region)

        from django.db.models import Sum, Max, Min
        
        stats = queryset.aggregate(
            total_capacity=Sum('capacity'),
            avg_capacity=Avg('capacity'),
            max_capacity=Max('capacity'),
            min_capacity=Min('capacity'),
            schools_with_capacity=Count('id')
        )

        return stats

    @staticmethod
    def exists_by_code(*, code: str, exclude_id: int = None) -> bool:
        """
        Check if a school exists with the given code.

        Args:
            code: School code to check
            exclude_id: Exclude school with this ID

        Returns:
            True if school exists with the code
        """
        queryset = School.objects.filter(code__iexact=code.strip())
        
        if exclude_id:
            queryset = queryset.exclude(id=exclude_id)
        
        return queryset.exists()

    @staticmethod
    def get_recent(*, limit: int = 10) -> QuerySet[School]:
        """
        Get recently created schools.

        Args:
            limit: Number of schools to return

        Returns:
            QuerySet of recent schools
        """
        return School.objects.order_by('-created_at')[:limit]

    @staticmethod
    def get_schools_needing_attention() -> QuerySet[School]:
        """
        Get schools that need attention (suspended or without staff).

        Returns:
            QuerySet of schools needing attention
        """
        return School.objects.filter(
            Q(status=SchoolStatus.SUSPENDED) |
            Q(status=SchoolStatus.ACTIVE, director__isnull=True, registrar__isnull=True)
        )
