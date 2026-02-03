"""
AdministrativeUnit service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.geography.models import RegionAdministrative, AdministrativeUnit
from domain.geography.constants import AdministrativeUnitType


class AdministrativeUnitService:
    """Service for administrative unit operations."""

    @staticmethod
    def create(*, region: RegionAdministrative, code: str, name: str,
               unit_type: str, parent: AdministrativeUnit = None, 
               user=None) -> AdministrativeUnit:
        """
        Create a new administrative unit.

        Args:
            region: Region this unit belongs to
            code: Short code
            name: Full name
            unit_type: Type (PREFECTURE, COMMUNE, SUBPREFECTURE)
            parent: Parent unit (required for SUBPREFECTURE)
            user: User performing the action

        Returns:
            Created AdministrativeUnit instance

        Raises:
            ValidationError: If hierarchy rules are violated
        """
        unit = AdministrativeUnit(
            region=region,
            code=code.upper().strip(),
            name=name.strip(),
            type=unit_type,
            parent=parent
        )
        # Validation happens in model's save method
        unit.save_by(user=user)
        return unit

    @staticmethod
    def update(*, unit: AdministrativeUnit, code: str = None, name: str = None,
               unit_type: str = None, parent: AdministrativeUnit = None,
               user=None) -> AdministrativeUnit:
        """
        Update an administrative unit.

        Args:
            unit: Unit instance to update
            code: New code (optional)
            name: New name (optional)
            unit_type: New type (optional)
            parent: New parent (optional)
            user: User performing the action

        Returns:
            Updated AdministrativeUnit instance

        Raises:
            ValidationError: If hierarchy rules are violated
        """
        if code is not None:
            unit.code = code.upper().strip()
        if name is not None:
            unit.name = name.strip()
        if unit_type is not None:
            unit.type = unit_type
        if parent is not None:
            unit.parent = parent

        # Validation happens in model's save method
        unit.save_by(user=user)
        return unit

    @staticmethod
    def delete(*, unit: AdministrativeUnit, user=None, hard: bool = False) -> None:
        """
        Delete an administrative unit (soft delete by default).

        Args:
            unit: Unit instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If unit has associated localities or child units
        """
        # Check for child units
        if unit.children.filter(is_deleted=False).exists():
            raise ValidationError(
                _('Cannot delete administrative unit with child units. '
                  'Delete or reassign all child units first.')
            )

        # Check for localities
        if unit.localities.filter(is_deleted=False).exists():
            raise ValidationError(
                _('Cannot delete administrative unit with associated localities. '
                  'Delete or reassign all localities first.')
            )

        if hard:
            unit.hard_delete()
        else:
            unit.soft_delete(user=user)

    @staticmethod
    def restore(*, unit: AdministrativeUnit, user=None) -> AdministrativeUnit:
        """
        Restore a soft-deleted administrative unit.

        Args:
            unit: Unit instance to restore
            user: User performing the action

        Returns:
            Restored AdministrativeUnit instance
        """
        unit.restore(user=user)
        return unit

    @staticmethod
    def get_hierarchy(unit: AdministrativeUnit) -> list[AdministrativeUnit]:
        """
        Get the full hierarchy from top to this unit.

        Args:
            unit: The administrative unit

        Returns:
            List of units from root to this unit
        """
        hierarchy = [unit]
        current = unit
        
        while current.parent:
            hierarchy.insert(0, current.parent)
            current = current.parent
        
        return hierarchy
