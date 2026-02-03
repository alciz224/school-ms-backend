"""
Country selectors.
"""

from django.db.models import QuerySet, Count

from domain.geography.models import Country


class CountrySelector:
    """Selector for country queries."""

    @staticmethod
    def get_all(*, include_deleted: bool = False) -> QuerySet[Country]:
        """
        Get all countries.

        Args:
            include_deleted: If True, include soft-deleted countries

        Returns:
            QuerySet of countries
        """
        if include_deleted:
            return Country.all_objects.all()
        return Country.objects.all()

    @staticmethod
    def get_by_id(*, country_id: int, include_deleted: bool = False) -> Country | None:
        """
        Get a country by ID.

        Args:
            country_id: Country ID
            include_deleted: If True, include soft-deleted countries

        Returns:
            Country instance or None
        """
        manager = Country.all_objects if include_deleted else Country.objects
        return manager.filter(id=country_id).first()

    @staticmethod
    def get_by_code(*, code: str, include_deleted: bool = False) -> Country | None:
        """
        Get a country by code.

        Args:
            code: Country code
            include_deleted: If True, include soft-deleted countries

        Returns:
            Country instance or None
        """
        manager = Country.all_objects if include_deleted else Country.objects
        return manager.filter(code__iexact=code.strip()).first()

    @staticmethod
    def search(*, query: str, include_deleted: bool = False) -> QuerySet[Country]:
        """
        Search countries by name or code.

        Args:
            query: Search query
            include_deleted: If True, include soft-deleted countries

        Returns:
            QuerySet of matching countries
        """
        manager = Country.all_objects if include_deleted else Country.objects
        return manager.filter(
            models.Q(name__icontains=query) | models.Q(code__icontains=query)
        )

    @staticmethod
    def get_with_region_counts() -> QuerySet[Country]:
        """
        Get all countries with their region counts.

        Returns:
            QuerySet of countries annotated with region_count
        """
        return Country.objects.annotate(
            region_count=Count('regions', filter=models.Q(regions__is_deleted=False))
        )


# Import models for Q objects
from django.db import models
