"""
AcademicYear service.
"""

from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction

from domain.academic.models import AcademicYear
from domain.academic.constants import AcademicYearStatus


class AcademicYearService:
    """Service for academic year operations."""

    @staticmethod
    def create(*, start_year: int, end_year: int = None, code: str = None, 
               status: str = AcademicYearStatus.DRAFT, is_current: bool = False, 
               user=None) -> AcademicYear:
        """
        Create a new academic year.

        Args:
            start_year: Starting year (e.g., 2024)
            end_year: Ending year (defaults to start_year + 1)
            code: Custom code (auto-generated if not provided)
            status: Academic year status
            is_current: Whether this is the current year
            user: User performing the action

        Returns:
            Created AcademicYear instance
        """
        if end_year is None:
            end_year = start_year + 1

        academic_year = AcademicYear(
            start_year=start_year,
            end_year=end_year,
            code=code,
            status=status,
            is_current=is_current,
            created_by=user
        )
        
        # save() will handle validation and current year logic
        academic_year.save()
        return academic_year

    @staticmethod
    def update(*, academic_year: AcademicYear, start_year: int = None, 
               end_year: int = None, code: str = None, status: str = None,
               user=None) -> AcademicYear:
        """
        Update an academic year.

        Args:
            academic_year: AcademicYear instance to update
            start_year: New start year (optional)
            end_year: New end year (optional)  
            code: New code (optional)
            status: New status (optional)
            user: User performing the action

        Returns:
            Updated AcademicYear instance
        """
        if start_year is not None:
            academic_year.start_year = start_year
        if end_year is not None:
            academic_year.end_year = end_year
        if code is not None:
            academic_year.code = code
        if status is not None:
            academic_year.status = status
            
        academic_year.updated_by = user
        academic_year.save()
        return academic_year

    @staticmethod
    @transaction.atomic
    def set_current(*, academic_year: AcademicYear, user=None) -> AcademicYear:
        """
        Set an academic year as current (atomic operation).

        Args:
            academic_year: AcademicYear instance to set as current
            user: User performing the action

        Returns:
            Updated AcademicYear instance

        Raises:
            ValidationError: If year cannot be set as current
        """
        # Validate year can be current
        if academic_year.status == AcademicYearStatus.ARCHIVED:
            raise ValidationError(
                _("Cannot set archived academic year as current")
            )

        # Set as current (save() handles atomic current year switching)
        academic_year.is_current = True
        academic_year.updated_by = user
        academic_year.save()
        
        return academic_year

    @staticmethod
    def activate(*, academic_year: AcademicYear, user=None) -> AcademicYear:
        """
        Activate an academic year.

        Args:
            academic_year: AcademicYear instance to activate
            user: User performing the action

        Returns:
            Updated AcademicYear instance

        Raises:
            ValidationError: If year cannot be activated
        """
        if academic_year.status == AcademicYearStatus.ARCHIVED:
            raise ValidationError(
                _("Cannot activate an archived academic year")
            )

        academic_year.status = AcademicYearStatus.ACTIVE
        academic_year.updated_by = user
        academic_year.save(update_fields=["status", "updated_at", "updated_by"])
        
        return academic_year

    @staticmethod
    def archive(*, academic_year: AcademicYear, user=None) -> AcademicYear:
        """
        Archive an academic year.

        Args:
            academic_year: AcademicYear instance to archive
            user: User performing the action

        Returns:
            Updated AcademicYear instance
        """
        # If it's current, it will be automatically unset when archived
        academic_year.status = AcademicYearStatus.ARCHIVED
        academic_year.is_current = False
        academic_year.updated_by = user
        academic_year.save(update_fields=["status", "is_current", "updated_at", "updated_by"])
        
        return academic_year

    @staticmethod
    def delete(*, academic_year: AcademicYear, user=None, hard: bool = False) -> None:
        """
        Delete an academic year (soft delete by default).

        Args:
            academic_year: AcademicYear instance to delete
            user: User performing the action
            hard: If True, permanently delete

        Raises:
            ValidationError: If year has dependencies or is current
        """
        # Check if it's the current year
        if academic_year.is_current:
            raise ValidationError(
                _("Cannot delete the current academic year. "
                  "Set another year as current first.")
            )

        # TODO: Add dependency checks when school year models exist
        # Check for school years, enrollments, etc.

        if hard:
            academic_year.hard_delete()
        else:
            academic_year.deleted_by = user
            academic_year.delete()  # Uses soft delete

    @staticmethod
    def restore(*, academic_year: AcademicYear, user=None) -> AcademicYear:
        """
        Restore a soft-deleted academic year.

        Args:
            academic_year: AcademicYear instance to restore
            user: User performing the action

        Returns:
            Restored AcademicYear instance
        """
        academic_year.is_deleted = False
        academic_year.deleted_at = None
        academic_year.deleted_by = None
        academic_year.updated_by = user
        academic_year.save(update_fields=[
            "is_deleted", "deleted_at", "deleted_by", "updated_at", "updated_by"
        ])
        
        return academic_year