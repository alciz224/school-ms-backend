"""
Locality selectors.
"""

from django.db import models
from django.db.models import QuerySet

from domain.geography.models import (
    Country, 
    RegionAdministrative, 
    AdministrativeUnit, 
    Locality
)


class LocalitySelector:
    """Selector for locality queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Locality]:
        """
        Get all localities.

        Args:
            include_deleted: If True, include soft-deleted localities

        Returns:
            QuerySet of localities
        """
        if include_deleted:
            return Locality.all_objects.all()
        return Locality.objects.all()

    @staticmethod
    def get_by_id(*, locality_id: int, include_deleted: bool = False) -> Locality | None:
        """
        Get a locality by ID.

        Args:
            locality_id: Locality ID
            include_deleted: If True, include soft-deleted localities

        Returns:
            Locality instance or None
        """
        manager = Locality.all_objects if include_deleted else Locality.objects
        return manager.filter(id=locality_id).first()

    @staticmethod
    def get_by_administrative_unit(*, unit: AdministrativeUnit | int,
                                    include_deleted: bool = False) -> QuerySet[Locality]:
        """
        Get all localities for an administrative unit.

        Args:
            unit: Administrative unit instance or ID
            include_deleted: If True, include soft-deleted localities

        Returns:
            QuerySet of localities
        """
        unit_id = unit.id if isinstance(unit, AdministrativeUnit) else unit
        manager = Locality.all_objects if include_deleted else Locality.objects
        return manager.filter(administrative_unit_id=unit_id)

    @staticmethod
    def get_by_region(*, region: RegionAdministrative | int,
                      include_deleted: bool = False) -> QuerySet[Locality]:
        """
        Get all localities in a region.

        Args:
            region: Region instance or ID
            include_deleted: If True, include soft-deleted localities

        Returns:
            QuerySet of localities
        """
        region_id = region.id if isinstance(region, RegionAdministrative) else region
        manager = Locality.all_objects if include_deleted else Locality.objects
        return manager.filter(administrative_unit__region_id=region_id)

    @staticmethod
    def get_by_country(*, country: Country | int,
                       include_deleted: bool = False) -> QuerySet[Locality]:
        """
        Get all localities in a country.

        Args:
            country: Country instance or ID
            include_deleted: If True, include soft-deleted localities

        Returns:
            QuerySet of localities
        """
        country_id = country.id if isinstance(country, Country) else country
        manager = Locality.all_objects if include_deleted else Locality.objects
        return manager.filter(administrative_unit__region__country_id=country_id)

    @staticmethod
    def search(*, query: str, unit: AdministrativeUnit | int = None,
               region: RegionAdministrative | int = None,
               country: Country | int = None,
               include_deleted: bool = False) -> QuerySet[Locality]:
        """
        Search localities by name or code.

        Args:
            query: Search query
            unit: Optional administrative unit to filter by
            region: Optional region to filter by
            country: Optional country to filter by
            include_deleted: If True, include soft-deleted localities

        Returns:
            QuerySet of matching localities
        """
        manager = Locality.all_objects if include_deleted else Locality.objects
        queryset = manager.filter(
            models.Q(name__icontains=query) | models.Q(code__icontains=query)
        )
        
        if unit:
            unit_id = unit.id if isinstance(unit, AdministrativeUnit) else unit
            queryset = queryset.filter(administrative_unit_id=unit_id)
        elif region:
            region_id = region.id if isinstance(region, RegionAdministrative) else region
            queryset = queryset.filter(administrative_unit__region_id=region_id)
        elif country:
            country_id = country.id if isinstance(country, Country) else country
            queryset = queryset.filter(administrative_unit__region__country_id=country_id)
        
        return queryset

    @staticmethod
    def get_with_full_path(*, locality_id: int) -> dict | None:
        """
        Get a locality with its full geographic path.

        Args:
            locality_id: Locality ID

        Returns:
            Dictionary with locality data and full path, or None
        """
        locality = Locality.objects.select_related(
            'administrative_unit__parent',
            'administrative_unit__region__country'
        ).filter(id=locality_id).first()
        
        if not locality:
            return None
        
        unit = locality.administrative_unit
        region = unit.region
        country = region.country
        
        return {
            'id': locality.id,
            'code': locality.code,
            'name': locality.name,
            'full_path': locality.full_path,
            'hierarchy': {
                'country': {'id': country.id, 'code': country.code, 'name': country.name},
                'region': {'id': region.id, 'code': region.code, 'name': region.name},
                'parent_unit': {
                    'id': unit.parent.id, 
                    'code': unit.parent.code, 
                    'name': unit.parent.name,
                    'type': unit.parent.type
                } if unit.parent else None,
                'administrative_unit': {
                    'id': unit.id, 
                    'code': unit.code, 
                    'name': unit.name,
                    'type': unit.type
                },
            }
        }

    @staticmethod
    def get_by_code(*, unit: AdministrativeUnit | int, code: str,
                    include_deleted: bool = False) -> Locality | None:
        """
        Get a locality by code within an administrative unit.

        Args:
            unit: Administrative unit instance or ID
            code: Locality code
            include_deleted: If True, include soft-deleted localities

        Returns:
            Locality instance or None
        """
        unit_id = unit.id if isinstance(unit, AdministrativeUnit) else unit
        manager = Locality.all_objects if include_deleted else Locality.objects
        return manager.filter(
            administrative_unit_id=unit_id, 
            code__iexact=code.strip()
        ).first()
