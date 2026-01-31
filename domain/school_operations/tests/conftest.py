"""Shared fixtures for school_operations tests."""
import pytest
from django.utils import timezone

from domain.academic.models import AcademicYear, Cycle, TermType, Level, Track
from domain.account.models import CustomUser
from domain.geography.models import Country, RegionAdministrative, AdministrativeUnit, Locality
from domain.geography.constants import AdministrativeUnitType
from domain.school_operations.models import School, SchoolYear, SchoolYearCycle


@pytest.fixture
def user(db):
    """Create a test user."""
    return CustomUser.objects.create_user(
        email="test@example.com",
        password="testpass123",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def country(db):
    """Create a test country."""
    return Country.objects.create(
        code="CM",
        name="Cameroon",
    )


@pytest.fixture
def region(db, country):
    """Create a test region."""
    return RegionAdministrative.objects.create(
        country=country,
        code="CE",
        name="Centre",
    )


@pytest.fixture
def administrative_unit(db, region):
    """Create a test administrative unit."""
    return AdministrativeUnit.objects.create(
        region=region,
        code="MFOUNDI",
        name="Mfoundi",
        type=AdministrativeUnitType.PREFECTURE,
    )


@pytest.fixture
def locality(db, administrative_unit):
    """Create a test locality."""
    return Locality.objects.create(
        administrative_unit=administrative_unit,
        code="YDE",
        name="Yaoundé",
    )


@pytest.fixture
def school(db, locality):
    """Create a test school."""
    return School.objects.create(
        name="Test School",
        code="TEST001",
        locality=locality,
        school_type="PRIMARY",
        ownership="PUBLIC",
        status="ACTIVE",
        capacity=500,
    )


@pytest.fixture
def academic_year(db):
    """Create a test academic year."""
    return AcademicYear.objects.create(
        start_year=2024,
        end_year=2025,
    )


@pytest.fixture
def cycle(db):
    """Create a test cycle without tracks."""
    return Cycle.objects.create(
        code="PRI",
        name="Primaire",
        has_track=False,
    )


@pytest.fixture
def cycle_with_track(db):
    """Create a test cycle with tracks."""
    return Cycle.objects.create(
        code="LYC",
        name="Lycée",
        has_track=True,
    )


@pytest.fixture
def term_type_trimester(db):
    """Create a trimester term type."""
    return TermType.objects.create(
        code="TRIMESTER",
        name="Trimestre",
        period_count=3,
    )


@pytest.fixture
def term_type_semester(db):
    """Create a semester term type."""
    return TermType.objects.create(
        code="SEMESTER",
        name="Semestre",
        period_count=2,
    )


@pytest.fixture
def level_primary_1(db, cycle):
    """Create a primary level 1."""
    return Level.objects.create(
        code="1A",
        name="1ère année",
        cycle=cycle,
        order=1,
    )


@pytest.fixture
def level_primary_2(db, cycle):
    """Create a primary level 2."""
    return Level.objects.create(
        code="2A",
        name="2ème année",
        cycle=cycle,
        order=2,
    )


@pytest.fixture
def track_sm(db, cycle_with_track):
    """Create a Sciences Mathématiques track."""
    return Track.objects.create(
        code="SM",
        name="Sciences Mathématiques",
        cycle=cycle_with_track,
    )


@pytest.fixture
def track_se(db, cycle_with_track):
    """Create a Sciences Expérimentales track."""
    return Track.objects.create(
        code="SE",
        name="Sciences Expérimentales",
        cycle=cycle_with_track,
    )


@pytest.fixture
def level_lycee_terminale(db, cycle_with_track, track_sm):
    """Create a Terminale level with SM track."""
    return Level.objects.create(
        code="TER",
        name="Terminale",
        cycle=cycle_with_track,
        track=track_sm,
        order=3,
    )


@pytest.fixture
def school_year(db, school, academic_year):
    """Create a test school year."""
    now = timezone.now().date()
    return SchoolYear.objects.create(
        school=school,
        academic_year=academic_year,
        name="Test School Year 2024-2025",
        start_date=now,
        end_date=now + timezone.timedelta(days=365),
        capacity=500,
    )


@pytest.fixture
def school_year_cycle(db, school_year, cycle, term_type_trimester):
    """Create a test school year cycle."""
    return SchoolYearCycle.objects.create(
        school_year=school_year,
        cycle=cycle,
        term_type=term_type_trimester,
    )


@pytest.fixture
def school_year_cycle_with_track(db, school_year, cycle_with_track, term_type_semester):
    """Create a test school year cycle with tracks."""
    return SchoolYearCycle.objects.create(
        school_year=school_year,
        cycle=cycle_with_track,
        term_type=term_type_semester,
    )
