"""SchoolYearLevel service for write operations."""
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils import timezone

from domain.account.models import CustomUser
from domain.school_operations.models.school_year_level import SchoolYearLevel


class SchoolYearLevelService:
    """
    Service for managing SchoolYearLevel write operations.

    Handles:
        - Creating level configurations for school year cycles
        - Updating level configurations
        - Soft deleting level configurations
        - Business rule validation
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        school_year_cycle_id: int,
        level_id: int,
        track_id: Optional[int] = None,
        created_by: Optional[CustomUser] = None,
    ) -> SchoolYearLevel:
        """
        Create a new school year level configuration.

        Args:
            school_year_cycle_id: ID of the school year cycle
            level_id: ID of the level (master reference)
            track_id: ID of the track (optional, required for cycles with tracks)
            created_by: User creating the record

        Returns:
            SchoolYearLevel: The created instance

        Raises:
            ValidationError: If validation fails
        """
        school_year_level = SchoolYearLevel(
            school_year_cycle_id=school_year_cycle_id,
            level_id=level_id,
            track_id=track_id,
            created_by=created_by,
            updated_by=created_by,
        )

        # full_clean is called in save() method
        school_year_level.save()

        return school_year_level

    @staticmethod
    @transaction.atomic
    def update(
        *,
        school_year_level: SchoolYearLevel,
        track_id: Optional[int] = None,
        updated_by: Optional[CustomUser] = None,
    ) -> SchoolYearLevel:
        """
        Update an existing school year level configuration.

        Note: school_year_cycle and level are immutable once created.
        Only track can be updated, and only if no classrooms or subjects exist.

        Args:
            school_year_level: Instance to update
            track_id: New track ID (optional)
            updated_by: User performing the update

        Returns:
            SchoolYearLevel: The updated instance

        Raises:
            ValidationError: If validation fails or has dependencies
        """
        if track_id is not None:
            # Check if there are dependencies (classrooms or subjects)
            # Placeholder for when Classroom and SchoolYearLevelSubject are implemented
            # if school_year_level.classrooms.exists():
            #     raise ValidationError(
            #         "Cannot change track when classrooms are associated with this level"
            #     )
            # if school_year_level.subjects.exists():
            #     raise ValidationError(
            #         "Cannot change track when subjects are associated with this level"
            #     )

            school_year_level.track_id = track_id

        if updated_by:
            school_year_level.updated_by = updated_by

        school_year_level.save()

        return school_year_level

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        school_year_level: SchoolYearLevel,
        deleted_by: Optional[CustomUser] = None,
    ) -> SchoolYearLevel:
        """
        Soft delete a school year level configuration.

        Args:
            school_year_level: Instance to delete
            deleted_by: User performing the deletion

        Returns:
            SchoolYearLevel: The soft-deleted instance

        Raises:
            ValidationError: If level has associated classrooms, subjects, or enrollments
        """
        # Check if can be deleted
        if not school_year_level.can_delete():
            raise ValidationError(
                "Cannot delete level configuration with associated classrooms, subjects, or enrollments"
            )

        school_year_level.is_deleted = True
        school_year_level.is_active = False
        school_year_level.deleted_by = deleted_by
        school_year_level.deleted_at = timezone.now()

        school_year_level.save(
            update_fields=["is_deleted", "is_active", "deleted_by", "deleted_at"]
        )

        return school_year_level

    @staticmethod
    @transaction.atomic
    def restore(
        *,
        school_year_level: SchoolYearLevel,
        updated_by: Optional[CustomUser] = None,
    ) -> SchoolYearLevel:
        """
        Restore a soft-deleted school year level configuration.

        Args:
            school_year_level: Instance to restore
            updated_by: User performing the restoration

        Returns:
            SchoolYearLevel: The restored instance

        Raises:
            ValidationError: If uniqueness constraint would be violated
        """
        school_year_level.is_deleted = False
        school_year_level.deleted_by = None
        school_year_level.deleted_at = None
        school_year_level.updated_by = updated_by

        school_year_level.save(
            update_fields=[
                "is_deleted",
                "deleted_by",
                "deleted_at",
                "updated_by",
                "updated_at",
            ]
        )

        return school_year_level

    @staticmethod
    @transaction.atomic
    def bulk_create_for_cycle(
        *,
        school_year_cycle_id: int,
        level_configs: list[dict],
        created_by: Optional[CustomUser] = None,
    ) -> list[SchoolYearLevel]:
        """
        Bulk create level configurations for a school year cycle.

        Args:
            school_year_cycle_id: ID of the school year cycle
            level_configs: List of dicts with 'level_id' and optional 'track_id'
            created_by: User creating the records

        Returns:
            list[SchoolYearLevel]: List of created instances

        Raises:
            ValidationError: If validation fails

        Example:
            level_configs = [
                {'level_id': 1, 'track_id': None},
                {'level_id': 2, 'track_id': None},
            ]
        """
        created_levels = []

        for config in level_configs:
            level = SchoolYearLevelService.create(
                school_year_cycle_id=school_year_cycle_id,
                level_id=config["level_id"],
                track_id=config.get("track_id"),
                created_by=created_by,
            )
            created_levels.append(level)

        return created_levels
