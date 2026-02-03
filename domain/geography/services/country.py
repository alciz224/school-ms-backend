"""
Country service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.geography.models import Country


class CountryService:
    """Service for country operations."""

    @staticmethod
    def create(*, code: str, name: str, description: str = None, user=None) -> Country:
        """
        Create a new country.

        Args:
            code: ISO or short code
            name: Full country name
            description: Optional description
            user: User performing the action

        Returns:
            Created Country instance
        """
        country = Country(
            code=code.upper().strip(),
            name=name.strip(),
            description=description
        )
        country.save_by(user=user)
        return country

    @staticmethod
    def update(*, country: Country, code: str = None, name: str = None, 
               description: str = None, user=None) -> Country:
        """
        Update a country.

        Args:
            country: Country instance to update
            code: New code (optional)
            name: New name (optional)
            description: New description (optional)
            user: User performing the action

        Returns:
            Updated Country instance
        """
        if code is not None:
            country.code = code.upper().strip()
        if name is not None:
            country.name = name.strip()
        if description is not None:
            country.description = description

        country.save_by(user=user)
        return country

    @staticmethod
    def delete(*, country: Country, user=None, hard: bool = False) -> None:
        """
        Delete a country (soft delete by default).

        Args:
            country: Country instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If country has associated regions
        """
        # Check for dependencies
        if country.regions.filter(is_deleted=False).exists():
            raise ValidationError(
                _('Cannot delete country with associated regions. '
                  'Delete or reassign all regions first.')
            )

        if hard:
            country.hard_delete()
        else:
            country.soft_delete(user=user)

    @staticmethod
    def restore(*, country: Country, user=None) -> Country:
        """
        Restore a soft-deleted country.

        Args:
            country: Country instance to restore
            user: User performing the action

        Returns:
            Restored Country instance
        """
        country.restore(user=user)
        return country
