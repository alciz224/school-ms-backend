"""
Locality service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.geography.models import AdministrativeUnit, Locality


class LocalityService:
    """Service for locality operations."""

    @staticmethod
    def create(*, administrative_unit: AdministrativeUnit, code: str, 
               name: str, user=None) -> Locality:
        """
        Create a new locality.

        Args:
            administrative_unit: Unit this locality belongs to
            code: Short code
            name: Full name
            user: User performing the action

        Returns:
            Created Locality instance
        """
        locality = Locality(
            administrative_unit=administrative_unit,
            code=code.upper().strip(),
            name=name.strip()
        )
        locality.save_by(user=user)
        return locality

    @staticmethod
    def update(*, locality: Locality, code: str = None, name: str = None,
               administrative_unit: AdministrativeUnit = None,
               user=None) -> Locality:
        """
        Update a locality.

        Args:
            locality: Locality instance to update
            code: New code (optional)
            name: New name (optional)
            administrative_unit: New administrative unit (optional)
            user: User performing the action

        Returns:
            Updated Locality instance
        """
        if code is not None:
            locality.code = code.upper().strip()
        if name is not None:
            locality.name = name.strip()
        if administrative_unit is not None:
            locality.administrative_unit = administrative_unit

        locality.save_by(user=user)
        return locality

    @staticmethod
    def delete(*, locality: Locality, user=None, hard: bool = False) -> None:
        """
        Delete a locality (soft delete by default).

        Args:
            locality: Locality instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If locality has associated schools (future check)
        """
        # Check for associated schools
        from domain.school_operations.models import School
        if School.objects.filter(locality=locality, is_deleted=False).exists():
            raise ValidationError(
                _('Cannot delete locality with associated schools. '
                  'Delete or reassign all schools first.')
            )

        if hard:
            locality.hard_delete()
        else:
            locality.soft_delete(user=user)

    @staticmethod
    def restore(*, locality: Locality, user=None) -> Locality:
        """
        Restore a soft-deleted locality.

        Args:
            locality: Locality instance to restore
            user: User performing the action

        Returns:
            Restored Locality instance
        """
        locality.restore(user=user)
        return locality
