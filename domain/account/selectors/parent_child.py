"""Parent-Child relationship selectors."""

from typing import Optional, List
from django.db.models import QuerySet

from domain.account.models import ParentChild, ParentProfile, StudentProfile


class ParentChildSelector:
    """Selector for parent-child relationship queries."""

    @staticmethod
    def list(
        *,
        parent_id: int | None = None,
        child_id: int | None = None,
        relationship_type: str | None = None,
        is_primary: bool | None = None,
    ) -> QuerySet[ParentChild]:
        """
        List parent-child relationships with optional filters.

        Args:
            parent_id: Filter by parent user ID
            child_id: Filter by child user ID
            relationship_type: Filter by relationship type
            is_primary: Filter by primary status

        Returns:
            QuerySet of ParentChild relationships
        """
        qs = ParentChild.objects.select_related("parent", "child")
        
        if parent_id:
            qs = qs.filter(parent_id=parent_id)
        if child_id:
            qs = qs.filter(child_id=child_id)
        if relationship_type:
            qs = qs.filter(relationship_type=relationship_type)
        if is_primary is not None:
            qs = qs.filter(is_primary=is_primary)
        
        return qs

    @staticmethod
    def get_by_id(*, relationship_id: int) -> ParentChild:
        """
        Get a parent-child relationship by ID.

        Args:
            relationship_id: Relationship ID

        Returns:
            ParentChild instance
        """
        return ParentChild.objects.select_related("parent", "child").get(id=relationship_id)

    @staticmethod
    def get_children(*, parent_id: int) -> QuerySet[StudentProfile]:
        """
        Get all children (StudentProfiles) for a parent.

        Args:
            parent_id: ParentProfile ID

        Returns:
            QuerySet of StudentProfile
        """
        return StudentProfile.objects.filter(
            parent_relationships__parent_id=parent_id,
            parent_relationships__is_deleted=False,
        ).distinct()

    @staticmethod
    def get_children_ids(*, parent_id: int) -> List[int]:
        """
        Get IDs of all children for a parent.

        Args:
            parent_id: Parent user ID

        Returns:
            List of child user IDs
        """
        return list(
            ParentChild.objects.filter(
                parent_id=parent_id,
                is_deleted=False,
            ).values_list("child_id", flat=True)
        )

    @staticmethod
    def get_parents(*, child_id: int) -> QuerySet[ParentProfile]:
        """
        Get all parents (ParentProfiles) for a child.

        Args:
            child_id: StudentProfile ID

        Returns:
            QuerySet of ParentProfile
        """
        return ParentProfile.objects.filter(
            children_relationships__child_id=child_id,
            children_relationships__is_deleted=False,
        ).distinct()

    @staticmethod
    def get_primary_parent(*, child_id: int) -> Optional[ParentProfile]:
        """
        Get the primary parent for a child.

        Args:
            child_id: StudentProfile ID

        Returns:
            Primary ParentProfile or None
        """
        relationship = ParentChild.objects.filter(
            child_id=child_id,
            is_primary=True,
            is_deleted=False,
        ).select_related("parent").first()
        
        return relationship.parent if relationship else None

    @staticmethod
    def has_relationship(*, parent_id: int, child_id: int) -> bool:
        """
        Check if a parent-child relationship exists.

        Args:
            parent_id: Parent user ID
            child_id: Child user ID

        Returns:
            True if relationship exists
        """
        return ParentChild.objects.filter(
            parent_id=parent_id,
            child_id=child_id,
            is_deleted=False,
        ).exists()
