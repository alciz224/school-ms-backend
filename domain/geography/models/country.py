"""
Country model.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.geography.models.base import GeographyBaseModel


class Country(GeographyBaseModel):
    """
    Represents a country.

    A country is the top-level geographic entity that contains regions.
    It serves as a global reference for schools and localities.

    Attributes:
        code: ISO or short code (e.g., 'GN' for Guinea)
        name: Full country name (e.g., 'Guinea')
        description: Optional description
    """

    code = models.CharField(
        _("code"),
        max_length=10,
        unique=True,
        db_index=True,
        help_text=_("ISO or short code (e.g., GN)"),
    )
    name = models.CharField(
        _("name"), max_length=100, unique=True, help_text=_("Full country name")
    )
    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        verbose_name = _("country")
        verbose_name_plural = _("countries")
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.name} ({self.code})"

    @property
    def regions_count(self) -> int:
        """
        Return the count of non-deleted regions.
        
        If the queryset was annotated with regions_count, use that value.
        Otherwise, perform a database query.
        """
        # Check if value was annotated (set as an attribute)
        if hasattr(self, '_regions_count'):
            return self._regions_count
        # Fallback to database query
        return self.regions.filter(is_deleted=False).count()
    
    @regions_count.setter
    def regions_count(self, value: int) -> None:
        """Allow Django ORM to set annotated value."""
        self._regions_count = value
