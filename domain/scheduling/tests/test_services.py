"""Tests for Schedule services."""

from datetime import date

import pytest
from django.core.exceptions import ValidationError

from domain.scheduling.constants import ScheduleStatus, DayOfWeek
from domain.scheduling.models import Schedule
from domain.scheduling.services import ScheduleService, ScheduleConflictError


@pytest.mark.django_db
class TestScheduleService:
    """Tests for ScheduleService."""

    def test_create_schedule(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test creating a schedule."""
        schedule = ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.DRAFT,
        })
        
        assert schedule.id is not None
        assert schedule.status == ScheduleStatus.DRAFT

    def test_create_with_conflict_detection(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test conflict detection when creating schedule."""
        # Create first schedule (ACTIVE)
        ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.ACTIVE,
        })
        
        # Try to create conflicting schedule
        with pytest.raises(ScheduleConflictError):
            ScheduleService.create(data={
                'school_year_id': school_year.id,
                'school_year_cycle_id': school_year_cycle.id,
                'classroom_id': classroom.id,
                'teacher_assignment_id': teacher_assignment.id,
                'day_of_week': DayOfWeek.MONDAY,
                'time_slot_id': time_slot_1.id,
                'effective_from': date(2024, 9, 1),
                'status': ScheduleStatus.ACTIVE,
            })

    def test_update_schedule(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
        time_slot_2,
    ):
        """Test updating a schedule."""
        schedule = ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.DRAFT,
        })
        
        updated = ScheduleService.update(
            schedule_id=schedule.id,
            data={'time_slot_id': time_slot_2.id}
        )
        
        assert updated.time_slot_id == time_slot_2.id

    def test_cannot_update_archived(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test cannot update archived schedule."""
        schedule = ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.ARCHIVED,
        })
        
        with pytest.raises(ValidationError):
            ScheduleService.update(
                schedule_id=schedule.id,
                data={'day_of_week': DayOfWeek.TUESDAY}
            )

    def test_delete_schedule(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test soft deleting a schedule."""
        schedule = ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.DRAFT,
        })
        
        ScheduleService.delete(schedule_id=schedule.id)
        
        schedule.refresh_from_db()
        assert schedule.is_deleted is True

    def test_change_status(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test changing schedule status."""
        schedule = ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.DRAFT,
        })
        
        updated = ScheduleService.change_status(
            schedule_id=schedule.id,
            new_status=ScheduleStatus.ACTIVE
        )
        
        assert updated.status == ScheduleStatus.ACTIVE

    def test_detect_conflicts(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test conflict detection."""
        # Create a schedule
        ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.ACTIVE,
        })
        
        # Detect conflicts
        conflicts = ScheduleService.detect_conflicts(
            classroom_id=classroom.id,
            teacher_assignment_id=teacher_assignment.id,
            day_of_week=DayOfWeek.MONDAY,
            time_slot_id=time_slot_1.id,
            effective_from=date(2024, 9, 1),
        )
        
        assert conflicts['has_conflicts'] is True
        assert len(conflicts['classroom_conflicts']) == 1

    def test_bulk_create(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
        time_slot_2,
    ):
        """Test bulk creating schedules."""
        schedules_data = [
            {
                'school_year_id': school_year.id,
                'school_year_cycle_id': school_year_cycle.id,
                'classroom_id': classroom.id,
                'teacher_assignment_id': teacher_assignment.id,
                'day_of_week': DayOfWeek.MONDAY,
                'time_slot_id': time_slot_1.id,
                'effective_from': date(2024, 9, 1),
                'status': ScheduleStatus.DRAFT,
            },
            {
                'school_year_id': school_year.id,
                'school_year_cycle_id': school_year_cycle.id,
                'classroom_id': classroom.id,
                'teacher_assignment_id': teacher_assignment.id,
                'day_of_week': DayOfWeek.TUESDAY,
                'time_slot_id': time_slot_2.id,
                'effective_from': date(2024, 9, 1),
                'status': ScheduleStatus.DRAFT,
            },
        ]
        
        result = ScheduleService.bulk_create(schedules_data=schedules_data)
        
        assert len(result['created']) == 2
        assert len(result['failed']) == 0
