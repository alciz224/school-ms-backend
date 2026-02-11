"""Tests for roster selectors."""

import datetime

import pytest

from domain.enrollment.selectors import RosterSelector
from domain.enrollment.services import StudentEnrollmentService


@pytest.mark.django_db
def test_get_classroom_roster(school_year_level, classroom_a):
    # Create 3 enrollments in classroom A
    for i in range(3):
        StudentEnrollmentService.create(
            first_name="Student",
            last_name=f"Test{i}",
            school_year_level=school_year_level,
            enrollment_date=datetime.date(2025, 9, 1),
            annual_identifier=f"AY-{i}",
            classroom=classroom_a,
            enrollment_status="ACTIVE",
        )

    roster = RosterSelector.get_classroom_roster(classroom_id=classroom_a.id)
    assert roster.count() == 3


@pytest.mark.django_db
def test_get_classroom_with_stats(school_year_level, classroom_a):
    classroom_a.capacity = 30
    classroom_a.save()

    # Create 2 active enrollments
    for i in range(2):
        StudentEnrollmentService.create(
            first_name="Student",
            last_name=f"Active{i}",
            school_year_level=school_year_level,
            enrollment_date=datetime.date(2025, 9, 1),
            annual_identifier=f"AY-ACTIVE-{i}",
            classroom=classroom_a,
            enrollment_status="ACTIVE",
        )

    classroom = RosterSelector.get_classroom_with_stats(classroom_id=classroom_a.id)
    assert classroom.student_count == 2
    assert classroom.capacity_remaining == 28
