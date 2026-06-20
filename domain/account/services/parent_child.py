"""Parent-Child relationship service."""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.account.models import ParentChild, ParentProfile, StudentProfile


class ParentChildService:
    """Service for parent-child relationship operations."""

    @staticmethod
    def create(
        *,
        parent: ParentProfile,
        child: StudentProfile,
        relationship_type: str = "GUARDIAN",
        is_primary: bool = False,
        notes: str = None,
        user=None
    ) -> ParentChild:
        """
        Create a parent-child relationship.

        Args:
            parent: Parent profile
            child: Student profile
            relationship_type: Type of relationship (FATHER, MOTHER, GUARDIAN, OTHER)
            is_primary: Whether this is the primary contact
            notes: Additional notes
            user: User performing the action

        Returns:
            Created ParentChild instance

        Raises:
            ValidationError: If relationship is invalid
        """
        relationship = ParentChild(
            parent=parent,
            child=child,
            relationship_type=relationship_type,
            is_primary=is_primary,
            notes=notes,
        )
        relationship.save_by(user=user)
        return relationship

    @staticmethod
    def update(
        *,
        relationship: ParentChild,
        relationship_type: str = None,
        is_primary: bool = None,
        notes: str = None,
        user=None
    ) -> ParentChild:
        """
        Update a parent-child relationship.

        Args:
            relationship: ParentChild instance to update
            relationship_type: New relationship type (optional)
            is_primary: New primary status (optional)
            notes: New notes (optional)
            user: User performing the action

        Returns:
            Updated ParentChild instance
        """
        if relationship_type is not None:
            relationship.relationship_type = relationship_type
        if is_primary is not None:
            relationship.is_primary = is_primary
        if notes is not None:
            relationship.notes = notes

        relationship.save_by(user=user)
        return relationship

    @staticmethod
    def delete(*, relationship: ParentChild, user=None, hard: bool = False) -> None:
        """
        Delete a parent-child relationship (soft delete by default).

        Args:
            relationship: ParentChild instance to delete
            user: User performing the action
            hard: If True, permanently delete

        """
        if hard:
            relationship.hard_delete()
        else:
            relationship.soft_delete(user=user)

    @staticmethod
    def restore(*, relationship: ParentChild, user=None) -> ParentChild:
        """
        Restore a soft-deleted parent-child relationship.

        Args:
            relationship: ParentChild instance to restore
            user: User performing the action

        Returns:
            Restored ParentChild instance
        """
        relationship.restore(user=user)
        return relationship

    @staticmethod
    def set_primary(*, relationship: ParentChild, user=None) -> ParentChild:
        """
        Set a relationship as primary and unset others for the same child.

        Args:
            relationship: ParentChild instance to set as primary
            user: User performing the action

        Returns:
            Updated ParentChild instance
        """
        # Unset other primary relationships for this child
        ParentChild.objects.filter(
            child=relationship.child,
            is_deleted=False
        ).exclude(id=relationship.id).update(is_primary=False)

        relationship.is_primary = True
        relationship.save_by(user=user)
        return relationship
