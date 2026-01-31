"""
SchoolYear service layer.

Business logic for SchoolYear operations.
"""

from datetime import timedelta
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from domain.school_operations.constants import (
    SchoolYearStatus,
    GUINEA_ACADEMIC_CALENDAR,
)
from domain.school_operations.models import School, SchoolYear
from domain.academic.models import AcademicYear


class SchoolYearService:
    """Service for SchoolYear business logic."""

    @staticmethod
    @transaction.atomic
    def create_school_year(
        school: School,
        academic_year: AcademicYear,
        start_date,
        end_date,
        enrollment_start_date=None,
        enrollment_end_date=None,
        capacity=None,
        description='',
        settings=None,
        user=None
    ) -> SchoolYear:
        """
        Create a new school year.
        
        Args:
            school: School instance
            academic_year: AcademicYear instance
            start_date: School year start date
            end_date: School year end date
            enrollment_start_date: Enrollment period start (optional)
            enrollment_end_date: Enrollment period end (optional)
            capacity: School year capacity (optional)
            description: Description (optional)
            settings: Custom settings (optional)
            user: User creating the school year
            
        Returns:
            SchoolYear: Created school year instance
            
        Raises:
            ValidationError: If validation fails
        """
        # Generate name and code
        name = f"{school.name} {academic_year.code}"
        
        # Use default settings if not provided
        if settings is None:
            settings = {}
        
        # Create school year
        school_year = SchoolYear(
            school=school,
            academic_year=academic_year,
            name=name,
            start_date=start_date,
            end_date=end_date,
            enrollment_start_date=enrollment_start_date,
            enrollment_end_date=enrollment_end_date,
            capacity=capacity,
            description=description,
            settings=settings,
            status=SchoolYearStatus.PLANNING,
        )
        
        school_year.save_by(user=user)
        
        return school_year

    @staticmethod
    @transaction.atomic
    def create_school_year_for_guinea(
        school: School,
        academic_year: AcademicYear,
        capacity=None,
        custom_settings=None,
        user=None
    ) -> SchoolYear:
        """
        Create a school year with Guinea's default calendar.
        
        Automatically sets dates based on Guinea's academic calendar
        (October to June).
        
        Args:
            school: School instance
            academic_year: AcademicYear instance
            capacity: School year capacity (optional)
            custom_settings: Custom settings to merge with defaults (optional)
            user: User creating the school year
            
        Returns:
            SchoolYear: Created school year instance
        """
        from datetime import date
        
        # Guinea's academic year: October to June
        start_month = GUINEA_ACADEMIC_CALENDAR['default_start_month']
        end_month = GUINEA_ACADEMIC_CALENDAR['default_end_month']
        
        # Start date: October 1st of start year
        start_date = date(academic_year.start_year, start_month, 1)
        
        # End date: June 30th of end year
        end_date = date(academic_year.end_year, end_month, 30)
        
        # Enrollment period: typically 4 weeks before start
        enrollment_weeks = GUINEA_ACADEMIC_CALENDAR['enrollment_period_weeks']
        enrollment_start_date = start_date - timedelta(weeks=enrollment_weeks)
        enrollment_end_date = start_date - timedelta(days=1)
        
        # Merge custom settings with defaults
        settings = {}
        if custom_settings:
            settings.update(custom_settings)
        
        return SchoolYearService.create_school_year(
            school=school,
            academic_year=academic_year,
            start_date=start_date,
            end_date=end_date,
            enrollment_start_date=enrollment_start_date,
            enrollment_end_date=enrollment_end_date,
            capacity=capacity,
            settings=settings,
            user=user
        )

    @staticmethod
    @transaction.atomic
    def update_school_year(
        school_year: SchoolYear,
        start_date=None,
        end_date=None,
        enrollment_start_date=None,
        enrollment_end_date=None,
        capacity=None,
        description=None,
        settings=None,
        user=None
    ) -> SchoolYear:
        """
        Update school year details.
        
        Args:
            school_year: SchoolYear instance to update
            start_date: New start date (optional)
            end_date: New end date (optional)
            enrollment_start_date: New enrollment start (optional)
            enrollment_end_date: New enrollment end (optional)
            capacity: New capacity (optional)
            description: New description (optional)
            settings: New settings (optional)
            user: User making the update
            
        Returns:
            SchoolYear: Updated school year instance
            
        Raises:
            ValidationError: If validation fails or year is archived
        """
        if school_year.status == SchoolYearStatus.ARCHIVED:
            raise ValidationError(
                _('Impossible de modifier une année scolaire archivée.')
            )
        
        # Update fields if provided
        if start_date is not None:
            school_year.start_date = start_date
        if end_date is not None:
            school_year.end_date = end_date
        if enrollment_start_date is not None:
            school_year.enrollment_start_date = enrollment_start_date
        if enrollment_end_date is not None:
            school_year.enrollment_end_date = enrollment_end_date
        if capacity is not None:
            school_year.capacity = capacity
        if description is not None:
            school_year.description = description
        if settings is not None:
            school_year.settings = settings
        
        school_year.save_by(user=user)
        
        return school_year

    @staticmethod
    @transaction.atomic
    def activate_school_year(school_year: SchoolYear, user=None) -> SchoolYear:
        """
        Activate a school year.
        
        Args:
            school_year: SchoolYear instance to activate
            user: User performing the action
            
        Returns:
            SchoolYear: Activated school year
            
        Raises:
            ValidationError: If activation fails
        """
        school_year.activate(user=user)
        return school_year

    @staticmethod
    @transaction.atomic
    def complete_school_year(school_year: SchoolYear, user=None) -> SchoolYear:
        """
        Mark school year as completed.
        
        Args:
            school_year: SchoolYear instance to complete
            user: User performing the action
            
        Returns:
            SchoolYear: Completed school year
            
        Raises:
            ValidationError: If completion fails
        """
        school_year.complete(user=user)
        return school_year

    @staticmethod
    @transaction.atomic
    def archive_school_year(school_year: SchoolYear, user=None) -> SchoolYear:
        """
        Archive a school year.
        
        Args:
            school_year: SchoolYear instance to archive
            user: User performing the action
            
        Returns:
            SchoolYear: Archived school year
            
        Raises:
            ValidationError: If archiving fails
        """
        school_year.archive(user=user)
        return school_year

    @staticmethod
    @transaction.atomic
    def delete_school_year(school_year: SchoolYear, user=None) -> None:
        """
        Soft delete a school year.
        
        Args:
            school_year: SchoolYear instance to delete
            user: User performing the action
            
        Raises:
            ValidationError: If deletion not allowed
        """
        can_delete, reason = school_year.can_be_deleted()
        
        if not can_delete:
            raise ValidationError(reason)
        
        school_year.soft_delete(user=user)

    @staticmethod
    def add_holiday_to_school_year(
        school_year: SchoolYear,
        name: str,
        start_date,
        end_date=None,
        user=None
    ) -> SchoolYear:
        """
        Add a holiday period to school year.
        
        Args:
            school_year: SchoolYear instance
            name: Holiday name
            start_date: Holiday start date
            end_date: Holiday end date (optional)
            user: User making the change
            
        Returns:
            SchoolYear: Updated school year
        """
        school_year.add_holiday(name, start_date, end_date, user=user)
        return school_year

    @staticmethod
    def update_school_year_setting(
        school_year: SchoolYear,
        key: str,
        value,
        user=None
    ) -> SchoolYear:
        """
        Update a specific school year setting.
        
        Args:
            school_year: SchoolYear instance
            key: Setting key (dot-notation)
            value: New value
            user: User making the change
            
        Returns:
            SchoolYear: Updated school year
        """
        school_year.update_setting(key, value, user=user)
        return school_year

    @staticmethod
    def get_enrollment_statistics(school_year: SchoolYear) -> dict:
        """
        Get enrollment statistics for a school year.
        
        Args:
            school_year: SchoolYear instance
            
        Returns:
            dict: Enrollment statistics
        """
        available = school_year.available_capacity()
        
        stats = {
            'total_capacity': school_year.capacity,
            'current_enrollment': school_year.current_enrollment_count,
            'available_capacity': available,
            'enrollment_percentage': 0,
            'is_full': False,
            'has_capacity': school_year.has_capacity(),
            'is_enrollment_open': school_year.is_enrollment_open(),
        }
        
        if school_year.capacity and school_year.capacity > 0:
            stats['enrollment_percentage'] = round(
                (school_year.current_enrollment_count / school_year.capacity) * 100,
                2
            )
            stats['is_full'] = school_year.current_enrollment_count >= school_year.capacity
        
        return stats

    @staticmethod
    def bulk_create_school_years_for_academic_year(
        academic_year: AcademicYear,
        schools: list[School],
        use_guinea_defaults=True,
        user=None
    ) -> list[SchoolYear]:
        """
        Create school years for multiple schools for a given academic year.
        
        Args:
            academic_year: AcademicYear instance
            schools: List of School instances
            use_guinea_defaults: Use Guinea's default calendar (default: True)
            user: User creating the school years
            
        Returns:
            list[SchoolYear]: Created school year instances
        """
        school_years = []
        
        for school in schools:
            # Skip if school year already exists
            if SchoolYear.objects.filter(
                school=school,
                academic_year=academic_year
            ).exists():
                continue
            
            try:
                if use_guinea_defaults:
                    school_year = SchoolYearService.create_school_year_for_guinea(
                        school=school,
                        academic_year=academic_year,
                        capacity=school.capacity,
                        user=user
                    )
                else:
                    # Would need explicit dates
                    continue
                
                school_years.append(school_year)
            except ValidationError:
                # Log error and continue
                continue
        
        return school_years
