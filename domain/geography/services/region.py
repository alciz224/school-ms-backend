"""
RegionAdministrative service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.geography.models import Country, RegionAdministrative


class RegionService:
    """Service for region operations."""

    @staticmethod
    def create(*, country: Country, code: str, name: str, 
               description: str = None, user=None) -> RegionAdministrative:
        """
        Create a new administrative region.

        Args:
            country: Country this region belongs to
            code: Short code
            name: Full region name
            description: Optional description
            user: User performing the action

        Returns:
            Created RegionAdministrative instance
        """
        region = RegionAdministrative(
            country=country,
            code=code.upper().strip(),
            name=name.strip(),
            description=description
        )
        region.save_by(user=user)
        return region

    @staticmethod
    def update(*, region: RegionAdministrative, code: str = None, name: str = None,
               description: str = None, user=None) -> RegionAdministrative:
        """
        Update a region.

        Args:
            region: Region instance to update
            code: New code (optional)
            name: New name (optional)
            description: New description (optional)
            user: User performing the action

        Returns:
            Updated RegionAdministrative instance
        """
        if code is not None:
            region.code = code.upper().strip()
        if name is not None:
            region.name = name.strip()
        if description is not None:
            region.description = description

        region.save_by(user=user)
        return region

    @staticmethod
    def delete(*, region: RegionAdministrative, user=None, hard: bool = False) -> None:
        """
        Delete a region (soft delete by default).

        Args:
            region: Region instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If region has associated administrative units
        """
        # Check for dependencies
        if region.administrative_units.filter(is_deleted=False).exists():
            raise ValidationError(
                _('Cannot delete region with associated administrative units. '
                  'Delete or reassign all units first.')
            )

        if hard:
            region.hard_delete()
        else:
            region.soft_delete(user=user)

    @staticmethod
    def restore(*, region: RegionAdministrative, user=None) -> RegionAdministrative:
        """
        Restore a soft-deleted region.

        Args:
            region: Region instance to restore
            user: User performing the action

        Returns:
            Restored RegionAdministrative instance
        """
        region.restore(user=user)
        return region
