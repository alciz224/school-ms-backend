"""Tests for Schedule API."""

from datetime import date

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from domain.scheduling.constants import ScheduleStatus, DayOfWeek
from domain.scheduling.models import Schedule
from domain.enrollment.models import StudentEnrollment


@pytest.mark.django_db
class TestScheduleAPI:
    """Tests for Schedule API endpoints."""

    def test_list_schedules(
        self,
        admin_user,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test listing schedules."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ACTIVE,
        )
        
        response = client.get('/api/v1/scheduling/schedules/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1

    def test_create_schedule(
        self,
        admin_user,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test creating a schedule."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        data = {
            'school_year': school_year.id,
            'school_year_cycle': school_year_cycle.id,
            'classroom': classroom.id,
            'teacher_assignment': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot': time_slot_1.id,
            'effective_from': '2024-09-01',
            'status': ScheduleStatus.DRAFT,
        }
        
        response = client.post('/api/v1/scheduling/schedules/', data)
        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data

    def test_update_schedule(
        self,
        admin_user,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test updating a schedule."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
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
        
        data = {'day_of_week': DayOfWeek.TUESDAY}
        response = client.patch(f'/api/v1/scheduling/schedules/{schedule.id}/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['day_of_week'] == DayOfWeek.TUESDAY

    def test_delete_schedule(
        self,
        admin_user,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test deleting a schedule."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
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
        
        response = client.delete(f'/api/v1/scheduling/schedules/{schedule.id}/')
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        schedule.refresh_from_db()
        assert schedule.is_deleted is True

    def test_classroom_timetable(
        self,
        admin_user,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test getting classroom timetable."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ACTIVE,
        )
        
        response = client.get(f'/api/v1/scheduling/timetables/classroom/{classroom.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_teacher_schedule(
        self,
        teacher,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test getting teacher schedule."""
        client = APIClient()
        client.force_authenticate(user=teacher)
        
        Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ACTIVE,
        )
        
        response = client.get(f'/api/v1/scheduling/timetables/teacher/{teacher.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_student_timetable(
        self,
        student,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test getting student timetable."""
        client = APIClient()
        client.force_authenticate(user=student)
        
        # Enroll student
        StudentEnrollment.objects.create(
            student=student,
            classroom=classroom,
            school_year_level=classroom.school_year_level,
            enrollment_status="ACTIVE",
            enrollment_date=date(2024, 9, 1),
        )
        
        Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ACTIVE,
        )
        
        response = client.get(f'/api/v1/scheduling/timetables/student/{student.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0

    def test_conflict_check(
        self,
        admin_user,
        school_year,
        school_year_cycle,
        classroom,
        teacher_assignment,
        time_slot_1,
    ):
        """Test conflict checking."""
        client = APIClient()
        client.force_authenticate(user=admin_user)
        
        # Create existing schedule
        Schedule.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_cycle,
            classroom=classroom,
            teacher_assignment=teacher_assignment,
            day_of_week=DayOfWeek.MONDAY,
            time_slot=time_slot_1,
            effective_from=date(2024, 9, 1),
            status=ScheduleStatus.ACTIVE,
        )
        
        # Check for conflicts
        data = {
            'classroom_id': classroom.id,
            'teacher_assignment_id': teacher_assignment.id,
            'day_of_week': DayOfWeek.MONDAY,
            'time_slot_id': time_slot_1.id,
            'effective_from': '2024-09-01',
        }
        
        response = client.post('/api/v1/scheduling/schedules/check-conflicts/', data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['has_conflicts'] is True
