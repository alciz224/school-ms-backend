"""
Locality model.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.geography.models.base import GeographyBaseModel


class Locality(GeographyBaseModel):
    """
    Represents a locality (village or neighborhood).

    A locality is the finest level of geographic division, belonging to
    an administrative unit. It serves as a reference for schools, students,
    and teachers.

    Attributes:
        administrative_unit: The administrative unit this locality belongs to
        code: Short code (e.g., 'KASSAPO', 'FILIMA')
        name: Full name (e.g., 'Kassapo', 'Filima')
    """

    administrative_unit = models.ForeignKey(
        'geography.AdministrativeUnit',
        on_delete=models.PROTECT,
        related_name='localities',
        verbose_name=_('administrative unit')
    )
    code = models.CharField(
        _('code'),
        max_length=20,
        db_index=True,
        help_text=_('Short code (e.g., KASSAPO)')
    )
    name = models.CharField(
        _('name'),
        max_length=100,
        help_text=_('Full name')
    )

    class Meta:
        verbose_name = _('locality')
        verbose_name_plural = _('localities')
        ordering = ['administrative_unit', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['administrative_unit', 'code'],
                condition=models.Q(is_deleted=False),
                name='unique_locality_code_per_unit'
            ),
            models.UniqueConstraint(
                fields=['administrative_unit', 'name'],
                condition=models.Q(is_deleted=False),
                name='unique_locality_name_per_unit'
            ),
        ]

    def __str__(self) -> str:
        return self.name

    @property
    def full_path(self) -> str:
        """Return the full geographic path from country to locality."""
        unit = self.administrative_unit
        region = unit.region
        country = region.country
        
        parts = [country.name, region.name]
        
        # Add parent unit if exists (for subprefectures)
        if unit.parent:
            parts.append(unit.parent.name)
        
        parts.extend([unit.name, self.name])
        
        return ' > '.join(parts)
