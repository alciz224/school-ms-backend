"""Tests for Schedule model."""

from datetime import date, timedelta

import pytest
from django.core.exceptions import ValidationError

from domain.enrollment.constants import TeacherAssignmentStatus
from domain.scheduling.constants import ScheduleStatus, DayOfWeek
from domain.scheduling.models import Schedule


@pytest.mark.django_db
class TestScheduleModel:
    """Tests for Schedule model."""

    def test_create_schedule(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test creating a valid schedule."""
        schedule = Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.DRAFT,
        )
        
        assert schedule.id is not None
        assert schedule.day_of_week == DayOfWeek.MONDAY
        assert schedule.status == ScheduleStatus.DRAFT
        assert schedule.is_active is False
        assert schedule.can_modify() is True

    def test_schedule_str(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test schedule string representation."""
        schedule = Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ACTIVE,
        )
        
        assert "Mathematics" in str(schedule)
        assert "Class 1A-A" in str(schedule)
        assert "Monday" in str(schedule)

    def test_teacher_assignment_must_be_active(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test that teacher assignment must be ACTIVE."""
        teacher_assignment.assignment_status = TeacherAssignmentStatus.ENDED
        teacher_assignment.end_date = date(2024, 12, 31)
        teacher_assignment.save()
        
        schedule = Schedule(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
        )
        
        with pytest.raises(ValidationError) as exc_info:
            schedule.full_clean()
        
        assert "teacher_assignment" in str(exc_info.value)

    def test_effective_dates_validation(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test effective dates validation."""
        schedule = Schedule(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 12, 1),
            effective_to=date(2024, 11, 1),  # Before effective_from
        )
        
        with pytest.raises(ValidationError) as exc_info:
            schedule.full_clean()
        
        assert "effective_to" in str(exc_info.value)

    def test_is_active_property(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test is_active property."""
        schedule = Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ACTIVE,
        )
        
        assert schedule.is_active is True
        
        schedule.status = ScheduleStatus.DRAFT
        assert schedule.is_active is False

    def test_is_archived_property(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test is_archived property."""
        schedule = Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ARCHIVED,
        )
        
        assert schedule.is_archived is True
        assert schedule.can_modify() is False
        assert schedule.can_delete() is False

    def test_shortcut_properties(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        teacher,
        subject,
        time_slot_1,
    ):
        """Test shortcut properties."""
        schedule = Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
        )
        
        assert schedule.teacher == teacher
        assert schedule.subject == subject
