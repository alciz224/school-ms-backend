"""Test fixtures for geography domain."""
import pytest
from django.contrib.auth import get_user_model

from domain.geography.models import (
    Country,
    RegionAdministrative,
    AdministrativeUnit,
    Locality,
)
from domain.geography.constants import AdministrativeUnitType

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
def country(db, user):
    """Create a test country."""
    from domain.geography.services import CountryService
    return CountryService.create(
        code="GN",
        name="Guinea",
        description="Republic of Guinea",
        user=user,
    )


@pytest.fixture
def region(db, country, user):
    """Create a test region."""
    from domain.geography.services import RegionService
    return RegionService.create(
        country=country,
        code="BOKE",
        name="Boké",
        description="Boké Region",
        user=user,
    )


@pytest.fixture
def prefecture(db, region, user):
    """Create a test prefecture."""
    from domain.geography.services import AdministrativeUnitService
    return AdministrativeUnitService.create(
        region=region,
        code="KAMSAR",
        name="Kamsar",
        type=AdministrativeUnitType.PREFECTURE,
        user=user,
    )


@pytest.fixture
def subprefecture(db, prefecture, user):
    """Create a test subprefecture."""
    from domain.geography.services import AdministrativeUnitService
    return AdministrativeUnitService.create(
        region=prefecture.region,
        parent=prefecture,
        code="KASSAPO",
        name="Kassapo",
        type=AdministrativeUnitType.SUBPREFECTURE,
        user=user,
    )


@pytest.fixture
def locality(db, prefecture, user):
    """Create a test locality."""
    from domain.geography.services import LocalityService
    return LocalityService.create(
        administrative_unit=prefecture,
        code="FILIMA",
        name="Filima",
        user=user,
    )
