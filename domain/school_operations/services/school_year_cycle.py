"""SchoolYearCycle service for write operations."""
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction

from domain.account.models import CustomUser
from domain.school_operations.models.school_year_cycle import SchoolYearCycle
from domain.shared.exceptions import BusinessRuleException


class SchoolYearCycleService:
    """
    Service for managing SchoolYearCycle write operations.

    Handles:
        - Creating cycle configurations for school years
        - Updating cycle configurations
        - Soft deleting cycle configurations
        - Business rule validation
    """

    @staticmethod
    @transaction.atomic
    def create(
        *,
        school_year_id: int,
        cycle_id: int,
        term_type_id: int,
        created_by: Optional[CustomUser] = None,
    ) -> SchoolYearCycle:
        """
        Create a new school year cycle configuration.

        Args:
            school_year_id: ID of the school year
            cycle_id: ID of the cycle (master reference)
            term_type_id: ID of the term type
            created_by: User creating the record

        Returns:
            SchoolYearCycle: The created instance

        Raises:
            ValidationError: If validation fails
        """
        school_year_cycle = SchoolYearCycle(
            school_year_id=school_year_id,
            cycle_id=cycle_id,
            term_type_id=term_type_id,
            created_by=created_by,
            updated_by=created_by,
        )

        # full_clean is called in save() method
        school_year_cycle.save()

        return school_year_cycle

    @staticmethod
    @transaction.atomic
    def update(
        *,
        school_year_cycle: SchoolYearCycle,
        term_type_id: Optional[int] = None,
        updated_by: Optional[CustomUser] = None,
    ) -> SchoolYearCycle:
        """
        Update an existing school year cycle configuration.

        Note: school_year and cycle are immutable once created.
        Only term_type can be updated, and only if no levels or assessments exist.

        Args:
            school_year_cycle: Instance to update
            term_type_id: New term type ID (optional)
            updated_by: User performing the update

        Returns:
            SchoolYearCycle: The updated instance

        Raises:
            ValidationError: If validation fails or has dependencies
        """
        if term_type_id is not None:
            # Check if there are dependencies (levels or assessments)
            # Placeholder for when SchoolYearLevel is implemented
            # if school_year_cycle.levels.exists():
            #     raise ValidationError(
            #         "Cannot change term_type when levels are associated with this cycle"
            #     )

            school_year_cycle.term_type_id = term_type_id

        if updated_by:
            school_year_cycle.updated_by = updated_by

        school_year_cycle.save()

        return school_year_cycle

    @staticmethod
    @transaction.atomic
    def delete(
        *,
        school_year_cycle: SchoolYearCycle,
        deleted_by: Optional[CustomUser] = None,
    ) -> SchoolYearCycle:
        """
        Soft delete a school year cycle configuration.

        Args:
            school_year_cycle: Instance to delete
            deleted_by: User performing the deletion

        Returns:
            SchoolYearCycle: The soft-deleted instance

        Raises:
            ValidationError: If cycle has associated levels or assessments
        """
        # Check if can be deleted
        if not school_year_cycle.can_delete():
            raise BusinessRuleException(
                message="Ce cycle est utilisé par des niveaux ou années scolaires et ne peut pas être retiré.",
                code="school_year_cycle_in_use",
                rule="school_year_cycle_can_delete",
            )

        from django.utils import timezone
        
        school_year_cycle.is_deleted = True
        school_year_cycle.is_active = False
        school_year_cycle.deleted_by = deleted_by
        school_year_cycle.deleted_at = timezone.now()

        school_year_cycle.save(update_fields=["is_deleted", "is_active", "deleted_by", "deleted_at"])

        return school_year_cycle

    @staticmethod
    @transaction.atomic
    def restore(
        *,
        school_year_cycle: SchoolYearCycle,
        updated_by: Optional[CustomUser] = None,
    ) -> SchoolYearCycle:
        """
        Restore a soft-deleted school year cycle configuration.

        Args:
            school_year_cycle: Instance to restore
            updated_by: User performing the restoration

        Returns:
            SchoolYearCycle: The restored instance

        Raises:
            ValidationError: If uniqueness constraint would be violated
        """
        school_year_cycle.is_deleted = False
        school_year_cycle.deleted_by = None
        school_year_cycle.deleted_at = None
        school_year_cycle.updated_by = updated_by

        school_year_cycle.save(
            update_fields=["is_deleted", "deleted_by", "deleted_at", "updated_by", "updated_at"]
        )

        return school_year_cycle

    @staticmethod
    @transaction.atomic
    def bulk_create_for_school_year(
        *,
        school_year_id: int,
        cycle_configs: list[dict],
        created_by: Optional[CustomUser] = None,
    ) -> list[SchoolYearCycle]:
        """
        Bulk create cycle configurations for a school year.

        Args:
            school_year_id: ID of the school year
            cycle_configs: List of dicts with 'cycle_id' and 'term_type_id'
            created_by: User creating the records

        Returns:
            list[SchoolYearCycle]: List of created instances

        Raises:
            ValidationError: If validation fails

        Example:
            cycle_configs = [
                {'cycle_id': 1, 'term_type_id': 1},
                {'cycle_id': 2, 'term_type_id': 2},
            ]
        """
        created_cycles = []

        for config in cycle_configs:
            cycle = SchoolYearCycleService.create(
                school_year_id=school_year_id,
                cycle_id=config["cycle_id"],
                term_type_id=config["term_type_id"],
                created_by=created_by,
            )
            created_cycles.append(cycle)

        return created_cycles
