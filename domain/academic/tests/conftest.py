"""Test fixtures for academic domain."""
import pytest
from django.contrib.auth import get_user_model

from domain.academic.models import (
    AcademicYear,
    Cycle,
    Track,
    Level,
    Subject,
    AssessmentType,
    TermType,
    Term,
)

User = get_user_model()


@pytest.fixture
def user(db):
    """Create a test user."""
    return User.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def academic_year(db, user):
    """Create a test academic year."""
    from domain.academic.services import AcademicYearService
    return AcademicYearService.create(
        start_year=2024,
        end_year=2025,
        user=user,
    )


@pytest.fixture
def cycle(db, user):
    """Create a test cycle."""
    from domain.academic.services import CycleService
    return CycleService.create(
        code="PRIM",
        name="Primaire",
        has_track=False,
        user=user,
    )


@pytest.fixture
def cycle_with_track(db, user):
    """Create a cycle that has tracks."""
    from domain.academic.services import CycleService
    return CycleService.create(
        code="SEC",
        name="Secondaire",
        has_track=True,
        user=user,
    )


@pytest.fixture
def track(db, cycle_with_track, user):
    """Create a test track."""
    from domain.academic.services import TrackService
    return TrackService.create(
        cycle=cycle_with_track,
        code="ST",
        name="Sciences et Technologies",
        user=user,
    )


@pytest.fixture
def level(db, cycle, user):
    """Create a test level."""
    from domain.academic.services import LevelService
    return LevelService.create(
        cycle=cycle,
        code="CP",
        name="Cours Préparatoire",
        order=1,
        user=user,
    )


@pytest.fixture
def subject(db, user):
    """Create a test subject."""
    from domain.academic.services import SubjectService
    return SubjectService.create(
        code="MATH",
        name="Mathématiques",
        user=user,
    )


@pytest.fixture
def assessment_type(db, user):
    """Create a test assessment type."""
    from domain.academic.services import AssessmentTypeService
    return AssessmentTypeService.create(
        code="EXAM",
        name="Examen",
        user=user,
    )


@pytest.fixture
def term_type(db, user):
    """Create a test term type."""
    from domain.academic.services import TermTypeService
    return TermTypeService.create(
        code="TRIM",
        name="Trimestre",
        number_of_terms=3,
        user=user,
    )


@pytest.fixture
def term(db, term_type, user):
    """Create a test term."""
    from domain.academic.services import TermService
    return TermService.create(
        term_type=term_type,
        order=1,
        code="T1",
        name="Premier Trimestre",
        user=user,
    )
