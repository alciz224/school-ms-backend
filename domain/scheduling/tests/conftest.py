"""Test fixtures for scheduling domain."""

from datetime import date, time, timedelta

import pytest
from django.utils import timezone

from domain.academic.models import (
    AcademicYear,
    Cycle,
    Level,
    Subject,
    TermType,
)
from domain.account.models import CustomUser
from domain.enrollment.models import Classroom, TeacherAssignment
from domain.geography.models import Country, RegionAdministrative, AdministrativeUnit, Locality
from domain.school_operations.models import (
    School,
    SchoolYear,
    SchoolYearCycle,
    SchoolYearCycleTimeSlot,
    SchoolYearLevel,
    SchoolYearLevelSubject,
    SchoolYearTeacher,
)
from domain.scheduling.constants import DayOfWeek, ScheduleStatus


@pytest.fixture
def country():
    """Create a test country."""
    return Country.objects.create(
        name="Guinea",
        code="GN",
    )


@pytest.fixture
def region(country):
    """Create a test region."""
    return RegionAdministrative.objects.create(
        name="Conakry",
        code="CKY",
        country=country,
    )


@pytest.fixture
def administrative_unit(region):
    """Create a test administrative unit."""
    return AdministrativeUnit.objects.create(
        name="Ratoma",
        code="RAT",
        region=region,
        type="COMMUNE",
    )


@pytest.fixture
def locality(administrative_unit):
    """Create a test locality."""
    return Locality.objects.create(
        name="Kaloum",
        code="KLM",
        administrative_unit=administrative_unit,
    )


@pytest.fixture
def school(locality):
    """Create a test school."""
    return School.objects.create(
        name="Test School",
        code="TS001",
        locality=locality,
        status="active",
    )


@pytest.fixture
def academic_year():
    """Create a test academic year."""
    return AcademicYear.objects.create(
        code="2024-2025",
        start_date=date(2024, 9, 1),
        end_date=date(2025, 6, 30),
        status="ACTIVE",
    )


@pytest.fixture
def cycle():
    """Create a test cycle."""
    return Cycle.objects.create(
        name="Primaire",
        code="PRIM",
        order=1,
    )


@pytest.fixture
def level(cycle):
    """Create a test level."""
    return Level.objects.create(
        name="1ère Année",
        code="1A",
        order=1,
        cycle=cycle,
    )


@pytest.fixture
def subject():
    """Create a test subject."""
    return Subject.objects.create(
        name="Mathematics",
        code="MATH",
    )


@pytest.fixture
def term_type():
    """Create a test term type."""
    return TermType.objects.create(
        name="Trimester",
        code="TRI",
        num_periods=3,
    )


@pytest.fixture
def school_year(school, academic_year):
    """Create a test school year."""
    return SchoolYear.objects.create(
        school=school,
        academic_year=academic_year,
        start_date=date(2024, 9, 1),
        end_date=date(2025, 6, 30),
        status="active",
    )


@pytest.fixture
def school_year_cycle(school_year, cycle, term_type):
    """Create a test school year cycle."""
    return SchoolYearCycle.objects.create(
        school_year=school_year,
        cycle=cycle,
        term_type=term_type,
    )


@pytest.fixture
def school_year_level(school_year_cycle, level):
    """Create a test school year level."""
    return SchoolYearLevel.objects.create(
        school_year_cycle=school_year_cycle,
        level=level,
    )


@pytest.fixture
def school_year_level_subject(school_year_level, subject):
    """Create a test school year level subject."""
    return SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level,
        subject=subject,
        coefficient=1.0,
    )


@pytest.fixture
def time_slot_1(school_year_cycle):
    """Create first time slot (8:00-9:00)."""
    return SchoolYearCycleTimeSlot.objects.create(
        school_year_cycle=school_year_cycle,
        name="Period 1",
        start_time=time(8, 0),
        end_time=time(9, 0),
        order=1,
        status="ACTIVE",
    )


@pytest.fixture
def time_slot_2(school_year_cycle):
    """Create second time slot (9:00-10:00)."""
    return SchoolYearCycleTimeSlot.objects.create(
        school_year_cycle=school_year_cycle,
        name="Period 2",
        start_time=time(9, 0),
        end_time=time(10, 0),
        order=2,
        status="ACTIVE",
    )


@pytest.fixture
def classroom(school_year_level):
    """Create a test classroom."""
    return Classroom.objects.create(
        school_year_level=school_year_level,
        name="Class 1A-A",
        capacity=30,
    )


@pytest.fixture
def teacher():
    """Create a test teacher user."""
    return CustomUser.objects.create_user(
        email="teacher@test.com",
        password="testpass123",
        first_name="John",
        last_name="Doe",
        role="TEACHER",
    )


@pytest.fixture
def school_year_teacher(school_year, teacher):
    """Create a test school year teacher."""
    return SchoolYearTeacher.objects.create(
        school_year=school_year,
        teacher=teacher,
        status="ACTIVE",
    )


@pytest.fixture
def teacher_assignment(school_year_teacher, classroom, school_year_level_subject):
    """Create a test teacher assignment."""
    return TeacherAssignment.objects.create(
        school_year_teacher=school_year_teacher,
        classroom=classroom,
        school_year_level_subject=school_year_level_subject,
        assignment_status="ACTIVE",
        start_date=date(2024, 9, 1),
    )


@pytest.fixture
def student():
    """Create a test student user."""
    return CustomUser.objects.create_user(
        email="student@test.com",
        password="testpass123",
        first_name="Jane",
        last_name="Smith",
        role="STUDENT",
    )


@pytest.fixture
def admin_user():
    """Create an admin user."""
    return CustomUser.objects.create_user(
        email="admin@test.com",
        password="testpass123",
        first_name="Admin",
        last_name="User",
        role="SCHOOL_ADMIN",
    )
