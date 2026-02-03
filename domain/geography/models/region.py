"""
RegionAdministrative model.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.geography.models.base import GeographyBaseModel


class RegionAdministrative(GeographyBaseModel):
    """
    Represents an administrative region within a country.

    A region is a subdivision of a country (e.g., 8 regions of Guinea + Conakry).
    It contains administrative units (prefectures, communes, subprefectures).

    Attributes:
        country: The country this region belongs to
        code: Short code (e.g., 'BOKE', 'CON')
        name: Full region name (e.g., 'Boké', 'Conakry')
        description: Optional description
    """

    country = models.ForeignKey(
        'geography.Country',
        on_delete=models.PROTECT,
        related_name='regions',
        verbose_name=_('country')
    )
    code = models.CharField(
        _('code'),
        max_length=20,
        db_index=True,
        help_text=_('Short code (e.g., BOKE)')
    )
    name = models.CharField(
        _('name'),
        max_length=100,
        help_text=_('Full region name')
    )
    description = models.TextField(
        _('description'),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _('administrative region')
        verbose_name_plural = _('administrative regions')
        ordering = ['country', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['country', 'code'],
                condition=models.Q(is_deleted=False),
                name='unique_region_code_per_country'
            ),
            models.UniqueConstraint(
                fields=['country', 'name'],
                condition=models.Q(is_deleted=False),
                name='unique_region_name_per_country'
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    @property
    def administrative_units_count(self) -> int:
        """
        Return the count of non-deleted administrative units.
        
        If the queryset was annotated with administrative_units_count, use that value.
        Otherwise, perform a database query.
        """
        # Check if value was annotated (set as an attribute)
        if hasattr(self, '_administrative_units_count'):
            return self._administrative_units_count
        # Fallback to database query
        return self.administrative_units.filter(is_deleted=False).count()
    
    @administrative_units_count.setter
    def administrative_units_count(self, value: int) -> None:
        """Allow Django ORM to set annotated value."""
        self._administrative_units_count = value
