import datetime

import pytest

from domain.academic.models import AcademicYear, Cycle, Level, TermType
from domain.enrollment.models import Classroom
from domain.geography.constants import AdministrativeUnitType
from domain.geography.models import (
    AdministrativeUnit,
    Country,
    Locality,
    RegionAdministrative,
)
from domain.school_operations.constants import SchoolType
from domain.school_operations.models import School, SchoolYear, SchoolYearCycle, SchoolYearLevel


@pytest.fixture
def school_year(db):
    country = Country.objects.create(code="GN", name="Guinea")
    region = RegionAdministrative.objects.create(country=country, code="CON", name="Conakry")
    unit = AdministrativeUnit.objects.create(
        region=region,
        code="KAL",
        name="Kaloum",
        type=AdministrativeUnitType.COMMUNE,
    )
    locality = Locality.objects.create(administrative_unit=unit, code="LOC", name="Locality")

    school = School.objects.create(
        name="Test School",
        code="TS-001",
        school_type=SchoolType.PRIMAIRE,
        locality=locality,
    )

    ay = AcademicYear.objects.create(
        start_year=2025,
        end_year=2026,
        status="ACTIVE",
    )

    return SchoolYear.objects.create(
        school=school,
        academic_year=ay,
        name="Test School Year 2025-2026",
        start_date=datetime.date(2025, 9, 1),
        end_date=datetime.date(2026, 7, 31),
        capacity=500,
    )


@pytest.fixture
def school_year_level(db, school_year):
    cycle = Cycle.objects.create(name="Primary", code="PRI")
    term_type = TermType.objects.create(name="Trimester", code="TRI", period_count=3)
    syc = SchoolYearCycle.objects.create(school_year=school_year, cycle=cycle, term_type=term_type)

    level = Level.objects.create(name="1st", code="L1", order=1, cycle=cycle)
    return SchoolYearLevel.objects.create(school_year_cycle=syc, level=level)


@pytest.fixture
def classroom_a(db, school_year_level):
    return Classroom.objects.create(school_year_level=school_year_level, name="A")


@pytest.fixture
def classroom_b(db, school_year_level):
    return Classroom.objects.create(school_year_level=school_year_level, name="B")
