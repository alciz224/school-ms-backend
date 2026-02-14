"""Tests for Schedule selectors."""

from datetime import date

import pytest

from domain.scheduling.constants import ScheduleStatus, DayOfWeek
from domain.scheduling.selectors import ScheduleSelector
from domain.scheduling.services import ScheduleService
from domain.enrollment.models import StudentEnrollment


@pytest.mark.django_db
class TestScheduleSelector:
    """Tests for ScheduleSelector."""

    def test_get_all(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test getting all schedules."""
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
        
        schedules = ScheduleSelector.get_all()
        assert schedules.count() == 1

    def test_get_by_classroom(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
        time_slot_2,
    ):
        """Test getting schedules by classroom."""
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
        
        ScheduleService.create(data={
            'school_year_id': school_year.id,
            'school_year_cycle_id': school_year_cycle.id,
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.TUESDAY,
            'time_slot_id': time_slot_2.id,
            'effective_from': date(2024, 9, 1),
            'status': ScheduleStatus.ACTIVE,
        })
        
        schedules = ScheduleSelector.get_by_classroom(classroom_id=classroom.id)
        assert schedules.count() == 2

    def test_get_by_teacher(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        teacher,
        time_slot_1,
    ):
        """Test getting schedules by teacher."""
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
        
        schedules = ScheduleSelector.get_by_teacher(teacher_id=teacher.id)
        assert schedules.count() == 1

    def test_get_by_student(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        student,
        time_slot_1,
    ):
        """Test getting schedules by student."""
        # Enroll student in classroom
        StudentEnrollment.objects.create(
            student=student,
            classroom=classroom,
            school_year_level=classroom.school_year_level,
            enrollment_status="ACTIVE",
            enrollment_date=date(2024, 9, 1),
        )
        
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
        
        schedules = ScheduleSelector.get_by_student(student_id=student.id)
        assert schedules.count() == 1

    def test_get_active_schedules(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test getting active schedules for a date."""
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
        
        schedules = ScheduleSelector.get_active_schedules(
            school_year_id=school_year.id,
            effective_date=date(2024, 10, 1),
        )
        assert schedules.count() == 1

    def test_get_conflicts(
        self,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test getting conflicting schedules."""
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
        
        conflicts = ScheduleSelector.get_conflicts(
            classroom_id=classroom.id,
            day_of_week=DayOfWeek.MONDAY,
            time_slot_id=time_slot_1.id,
            effective_from=date(2024, 9, 1),
        )
        assert conflicts.count() == 1
