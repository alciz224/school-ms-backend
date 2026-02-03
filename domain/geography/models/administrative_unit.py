"""
AdministrativeUnit model.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.geography.models.base import GeographyBaseModel
from domain.geography.constants import AdministrativeUnitType


class AdministrativeUnit(GeographyBaseModel):
    """
    Represents an administrative unit (prefecture, commune, or subprefecture).

    Administrative units are subdivisions of a region. They can have a hierarchical
    structure where subprefectures belong to prefectures.

    Hierarchy rules:
        - PREFECTURE: No parent (parent_id = NULL)
        - COMMUNE: No parent (parent_id = NULL)
        - SUBPREFECTURE: Must have a PREFECTURE parent

    Attributes:
        region: The region this unit belongs to
        parent: Parent administrative unit (for subprefectures)
        code: Short code (e.g., 'KAMSAR', 'KALOUM')
        name: Full name (e.g., 'Kamsar', 'Kaloum')
        type: Type of unit (PREFECTURE, COMMUNE, SUBPREFECTURE)
    """

    region = models.ForeignKey(
        'geography.RegionAdministrative',
        on_delete=models.PROTECT,
        related_name='administrative_units',
        verbose_name=_('region')
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='children',
        verbose_name=_('parent unit'),
        help_text=_('Parent administrative unit (required for subprefectures)')
    )
    code = models.CharField(
        _('code'),
        max_length=20,
        db_index=True,
        help_text=_('Short code (e.g., KAMSAR)')
    )
    name = models.CharField(
        _('name'),
        max_length=100,
        help_text=_('Full name')
    )
    type = models.CharField(
        _('type'),
        max_length=20,
        choices=AdministrativeUnitType.choices,
        db_index=True
    )

    class Meta:
        verbose_name = _('administrative unit')
        verbose_name_plural = _('administrative units')
        ordering = ['region', 'type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['region', 'code'],
                condition=models.Q(is_deleted=False),
                name='unique_unit_code_per_region'
            ),
            models.UniqueConstraint(
                fields=['region', 'name'],
                condition=models.Q(is_deleted=False),
                name='unique_unit_name_per_region'
            ),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_type_display()})"

    def clean(self) -> None:
        """Validate hierarchy rules."""
        super().clean()
        self._validate_hierarchy()

    def _validate_hierarchy(self) -> None:
        """
        Validate the parent-child hierarchy rules.

        Rules:
            - SUBPREFECTURE must have a parent that is a PREFECTURE
            - COMMUNE and PREFECTURE must not have a parent
        """
        if self.type == AdministrativeUnitType.SUBPREFECTURE:
            if not self.parent:
                raise ValidationError({
                    'parent': _('A subprefecture must have a parent prefecture.')
                })
            if self.parent.type != AdministrativeUnitType.PREFECTURE:
                raise ValidationError({
                    'parent': _('A subprefecture parent must be a prefecture.')
                })
            if self.parent.region_id != self.region_id:
                raise ValidationError({
                    'parent': _('Parent must belong to the same region.')
                })
        elif self.type in (AdministrativeUnitType.PREFECTURE, AdministrativeUnitType.COMMUNE):
            if self.parent:
                raise ValidationError({
                    'parent': _(f'A {self.get_type_display().lower()} cannot have a parent.')
                })

    def save(self, *args, **kwargs) -> None:
        """Save with validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def localities_count(self) -> int:
        """
        Return the count of non-deleted localities.
        
        If the queryset was annotated with localities_count, use that value.
        Otherwise, perform a database query.
        """
        # Check if value was annotated (set as an attribute)
        if hasattr(self, '_localities_count'):
            return self._localities_count
        # Fallback to database query
        return self.localities.filter(is_deleted=False).count()
    
    @localities_count.setter
    def localities_count(self, value: int) -> None:
        """Allow Django ORM to set annotated value."""
        self._localities_count = value

    @property
    def children_count(self) -> int:
        """
        Return the count of non-deleted child units.
        
        If the queryset was annotated with children_count, use that value.
        Otherwise, perform a database query.
        """
        # Check if value was annotated (set as an attribute)
        if hasattr(self, '_children_count'):
            return self._children_count
        # Fallback to database query
        return self.children.filter(is_deleted=False).count()
    
    @children_count.setter
    def children_count(self, value: int) -> None:
        """Allow Django ORM to set annotated value."""
        self._children_count = value
