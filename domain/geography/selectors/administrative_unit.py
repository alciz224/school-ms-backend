"""
AdministrativeUnit selectors.
"""

from django.db import models
from django.db.models import QuerySet, Count

from domain.geography.models import RegionAdministrative, AdministrativeUnit
from domain.geography.constants import AdministrativeUnitType


class AdministrativeUnitSelector:
    """Selector for administrative unit queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get all administrative units.

        Args:
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of administrative units
        """
        if include_deleted:
            return AdministrativeUnit.all_objects.all()
        return AdministrativeUnit.objects.all()

    @staticmethod
    def get_by_id(*, unit_id: int, include_deleted: bool = False) -> AdministrativeUnit | None:
        """
        Get an administrative unit by ID.

        Args:
            unit_id: Unit ID
            include_deleted: If True, include soft-deleted units

        Returns:
            AdministrativeUnit instance or None
        """
        manager = AdministrativeUnit.all_objects if include_deleted else AdministrativeUnit.objects
        return manager.filter(id=unit_id).first()

    @staticmethod
    def get_by_region(*, region: RegionAdministrative | int, 
                      include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get all administrative units for a region.

        Args:
            region: Region instance or ID
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of administrative units
        """
        region_id = region.id if isinstance(region, RegionAdministrative) else region
        manager = AdministrativeUnit.all_objects if include_deleted else AdministrativeUnit.objects
        return manager.filter(region_id=region_id)

    @staticmethod
    def get_by_type(*, unit_type: str, region: RegionAdministrative | int = None,
                    include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get administrative units by type.

        Args:
            unit_type: Type (PREFECTURE, COMMUNE, SUBPREFECTURE)
            region: Optional region to filter by
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of administrative units
        """
        manager = AdministrativeUnit.all_objects if include_deleted else AdministrativeUnit.objects
        queryset = manager.filter(type=unit_type)
        
        if region:
            region_id = region.id if isinstance(region, RegionAdministrative) else region
            queryset = queryset.filter(region_id=region_id)
        
        return queryset

    @staticmethod
    def get_prefectures(*, region: RegionAdministrative | int = None,
                        include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get all prefectures.

        Args:
            region: Optional region to filter by
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of prefectures
        """
        return AdministrativeUnitSelector.get_by_type(
            unit_type=AdministrativeUnitType.PREFECTURE,
            region=region,
            include_deleted=include_deleted
        )

    @staticmethod
    def get_communes(*, region: RegionAdministrative | int = None,
                     include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get all communes.

        Args:
            region: Optional region to filter by
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of communes
        """
        return AdministrativeUnitSelector.get_by_type(
            unit_type=AdministrativeUnitType.COMMUNE,
            region=region,
            include_deleted=include_deleted
        )

    @staticmethod
    def get_subprefectures(*, prefecture: AdministrativeUnit | int = None,
                           region: RegionAdministrative | int = None,
                           include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get all subprefectures.

        Args:
            prefecture: Optional parent prefecture to filter by
            region: Optional region to filter by
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of subprefectures
        """
        manager = AdministrativeUnit.all_objects if include_deleted else AdministrativeUnit.objects
        queryset = manager.filter(type=AdministrativeUnitType.SUBPREFECTURE)
        
        if prefecture:
            parent_id = prefecture.id if isinstance(prefecture, AdministrativeUnit) else prefecture
            queryset = queryset.filter(parent_id=parent_id)
        
        if region:
            region_id = region.id if isinstance(region, RegionAdministrative) else region
            queryset = queryset.filter(region_id=region_id)
        
        return queryset

    @staticmethod
    def get_children(*, parent: AdministrativeUnit | int,
                     include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get child units of a parent unit.

        Args:
            parent: Parent unit instance or ID
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of child administrative units
        """
        parent_id = parent.id if isinstance(parent, AdministrativeUnit) else parent
        manager = AdministrativeUnit.all_objects if include_deleted else AdministrativeUnit.objects
        return manager.filter(parent_id=parent_id)

    @staticmethod
    def get_root_units(*, region: RegionAdministrative | int = None,
                       include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Get root units (prefectures and communes with no parent).

        Args:
            region: Optional region to filter by
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of root administrative units
        """
        manager = AdministrativeUnit.all_objects if include_deleted else AdministrativeUnit.objects
        queryset = manager.filter(parent__isnull=True)
        
        if region:
            region_id = region.id if isinstance(region, RegionAdministrative) else region
            queryset = queryset.filter(region_id=region_id)
        
        return queryset

    @staticmethod
    def search(*, query: str, region: RegionAdministrative | int = None,
               unit_type: str = None, include_deleted: bool = False) -> QuerySet[AdministrativeUnit]:
        """
        Search administrative units by name or code.

        Args:
            query: Search query
            region: Optional region to filter by
            unit_type: Optional type to filter by
            include_deleted: If True, include soft-deleted units

        Returns:
            QuerySet of matching administrative units
        """
        manager = AdministrativeUnit.all_objects if include_deleted else AdministrativeUnit.objects
        queryset = manager.filter(
            models.Q(name__icontains=query) | models.Q(code__icontains=query)
        )
        
        if region:
            region_id = region.id if isinstance(region, RegionAdministrative) else region
            queryset = queryset.filter(region_id=region_id)
        
        if unit_type:
            queryset = queryset.filter(type=unit_type)
        
        return queryset

    @staticmethod
    def get_with_locality_counts(*, region: RegionAdministrative | int = None) -> QuerySet[AdministrativeUnit]:
        """
        Get administrative units with their locality counts.

        Args:
            region: Optional region to filter by

        Returns:
            QuerySet of units annotated with locality_count
        """
        queryset = AdministrativeUnit.objects.annotate(
            locality_count=Count('localities', filter=models.Q(localities__is_deleted=False))
        )
        
        if region:
            region_id = region.id if isinstance(region, RegionAdministrative) else region
            queryset = queryset.filter(region_id=region_id)
        
        return queryset
