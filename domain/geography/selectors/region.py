"""
RegionAdministrative selectors.
"""

from django.db import models
from django.db.models import QuerySet, Count

from domain.geography.models import Country, RegionAdministrative


class RegionSelector:
    """Selector for region queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[RegionAdministrative]:
        """
        Get all regions.

        Args:
            include_deleted: If True, include soft-deleted regions

        Returns:
            QuerySet of regions
        """
        if include_deleted:
            return RegionAdministrative.all_objects.all()
        return RegionAdministrative.objects.all()

    @staticmethod
    def get_by_id(*, region_id: int, include_deleted: bool = False) -> RegionAdministrative | None:
        """
        Get a region by ID.

        Args:
            region_id: Region ID
            include_deleted: If True, include soft-deleted regions

        Returns:
            RegionAdministrative instance or None
        """
        manager = RegionAdministrative.all_objects if include_deleted else RegionAdministrative.objects
        return manager.filter(id=region_id).first()

    @staticmethod
    def get_by_country(*, country: Country | int, include_deleted: bool = False) -> QuerySet[RegionAdministrative]:
        """
        Get all regions for a country.

        Args:
            country: Country instance or ID
            include_deleted: If True, include soft-deleted regions

        Returns:
            QuerySet of regions
        """
        country_id = country.id if isinstance(country, Country) else country
        manager = RegionAdministrative.all_objects if include_deleted else RegionAdministrative.objects
        return manager.filter(country_id=country_id)

    @staticmethod
    def get_by_code(*, country: Country | int, code: str, 
                    include_deleted: bool = False) -> RegionAdministrative | None:
        """
        Get a region by code within a country.

        Args:
            country: Country instance or ID
            code: Region code
            include_deleted: If True, include soft-deleted regions

        Returns:
            RegionAdministrative instance or None
        """
        country_id = country.id if isinstance(country, Country) else country
        manager = RegionAdministrative.all_objects if include_deleted else RegionAdministrative.objects
        return manager.filter(country_id=country_id, code__iexact=code.strip()).first()

    @staticmethod
    def search(*, query: str, country: Country | int = None, 
               include_deleted: bool = False) -> QuerySet[RegionAdministrative]:
        """
        Search regions by name or code.

        Args:
            query: Search query
            country: Optional country to filter by
            include_deleted: If True, include soft-deleted regions

        Returns:
            QuerySet of matching regions
        """
        manager = RegionAdministrative.all_objects if include_deleted else RegionAdministrative.objects
        queryset = manager.filter(
            models.Q(name__icontains=query) | models.Q(code__icontains=query)
        )
        
        if country:
            country_id = country.id if isinstance(country, Country) else country
            queryset = queryset.filter(country_id=country_id)
        
        return queryset

    @staticmethod
    def get_with_unit_counts(*, country: Country | int = None) -> QuerySet[RegionAdministrative]:
        """
        Get regions with their administrative unit counts.

        Args:
            country: Optional country to filter by

        Returns:
            QuerySet of regions annotated with unit_count
        """
        queryset = RegionAdministrative.objects.annotate(
            unit_count=Count('administrative_units', 
                           filter=models.Q(administrative_units__is_deleted=False))
        )
        
        if country:
            country_id = country.id if isinstance(country, Country) else country
            queryset = queryset.filter(country_id=country_id)
        
        return queryset
