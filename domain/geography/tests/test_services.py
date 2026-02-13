"""Tests for geography services."""
import pytest
from django.core.exceptions import ValidationError

from domain.geography.services import (
    CountryService,
    RegionService,
    AdministrativeUnitService,
    LocalityService,
)
from domain.geography.constants import AdministrativeUnitType


@pytest.mark.django_db
class TestCountryService:
    """Tests for CountryService."""

    def test_create_country(self, user):
        """Test creating a country."""
        country = CountryService.create(
            code="gn",  # Test case conversion
            name="  Guinea  ",  # Test trimming
            description="Republic of Guinea",
            user=user,
        )
        assert country.code == "GN"  # Uppercase
        assert country.name == "Guinea"  # Trimmed
        assert country.created_by == user

    def test_update_country(self, country, user):
        """Test updating a country."""
        updated = CountryService.update(
            country=country,
            code="GIN",
            name="Republic of Guinea",
            user=user,
        )
        assert updated.code == "GIN"
        assert updated.name == "Republic of Guinea"
        assert updated.updated_by == user

    def test_delete_country_with_regions(self, country, region, user):
        """Test that cannot delete country with associated regions."""
        with pytest.raises(ValidationError) as exc_info:
            CountryService.delete(country=country, user=user)
        assert "Cannot delete country with associated regions" in str(exc_info.value)

    def test_soft_delete_country(self, country, user):
        """Test soft deleting a country."""
        CountryService.delete(country=country, user=user)
        assert country.is_deleted is True
        assert country.deleted_by == user

    def test_restore_country(self, country, user):
        """Test restoring a soft-deleted country."""
        country.soft_delete(user=user)
        restored = CountryService.restore(country=country, user=user)
        assert restored.is_deleted is False


@pytest.mark.django_db
class TestRegionService:
    """Tests for RegionService."""

    def test_create_region(self, country, user):
        """Test creating a region."""
        region = RegionService.create(
            country=country,
            code="boke",  # Test case conversion
            name="  Boké  ",  # Test trimming
            description="Boké Region",
            user=user,
        )
        assert region.code == "BOKE"
        assert region.name == "Boké"
        assert region.country == country

    def test_update_region(self, region, user):
        """Test updating a region."""
        updated = RegionService.update(
            region=region,
            code="BK",
            name="Boké Region",
            user=user,
        )
        assert updated.code == "BK"
        assert updated.name == "Boké Region"

    def test_delete_region_with_units(self, region, prefecture, user):
        """Test that cannot delete region with administrative units."""
        with pytest.raises(ValidationError) as exc_info:
            RegionService.delete(region=region, user=user)
        assert "Cannot delete region with associated administrative units" in str(exc_info.value)

    def test_soft_delete_region(self, region, user):
        """Test soft deleting a region."""
        RegionService.delete(region=region, user=user)
        assert region.is_deleted is True


@pytest.mark.django_db
class TestAdministrativeUnitService:
    """Tests for AdministrativeUnitService."""

    def test_create_prefecture(self, region, user):
        """Test creating a prefecture."""
        prefecture = AdministrativeUnitService.create(
            region=region,
            code="kamsar",
            name="  Kamsar  ",
            type=AdministrativeUnitType.PREFECTURE,
            user=user,
        )
        assert prefecture.code == "KAMSAR"
        assert prefecture.name == "Kamsar"
        assert prefecture.type == AdministrativeUnitType.PREFECTURE
        assert prefecture.parent is None

    def test_create_subprefecture(self, prefecture, user):
        """Test creating a subprefecture."""
        subprefecture = AdministrativeUnitService.create(
            region=prefecture.region,
            parent=prefecture,
            code="KASSAPO",
            name="Kassapo",
            type=AdministrativeUnitType.SUBPREFECTURE,
            user=user,
        )
        assert subprefecture.parent == prefecture
        assert subprefecture.type == AdministrativeUnitType.SUBPREFECTURE

    def test_update_administrative_unit(self, prefecture, user):
        """Test updating an administrative unit."""
        updated = AdministrativeUnitService.update(
            unit=prefecture,
            name="Kamsar Prefecture",
            user=user,
        )
        assert updated.name == "Kamsar Prefecture"

    def test_delete_unit_with_localities(self, prefecture, locality, user):
        """Test that cannot delete unit with localities."""
        with pytest.raises(ValidationError) as exc_info:
            AdministrativeUnitService.delete(unit=prefecture, user=user)
        assert "Cannot delete administrative unit with associated localities" in str(exc_info.value)

    def test_delete_prefecture_with_children(self, prefecture, subprefecture, user):
        """Test that cannot delete prefecture with child units."""
        with pytest.raises(ValidationError) as exc_info:
            AdministrativeUnitService.delete(unit=prefecture, user=user)
        assert "Cannot delete administrative unit with child units" in str(exc_info.value)

    def test_soft_delete_unit(self, region, user):
        """Test soft deleting an administrative unit."""
        unit = AdministrativeUnitService.create(
            region=region,
            code="TEST",
            name="Test Unit",
            type=AdministrativeUnitType.COMMUNE,
            user=user,
        )
        AdministrativeUnitService.delete(unit=unit, user=user)
        assert unit.is_deleted is True


@pytest.mark.django_db
class TestLocalityService:
    """Tests for LocalityService."""

    def test_create_locality(self, prefecture, user):
        """Test creating a locality."""
        locality = LocalityService.create(
            administrative_unit=prefecture,
            code="filima",
            name="  Filima  ",
            user=user,
        )
        assert locality.code == "FILIMA"
        assert locality.name == "Filima"
        assert locality.administrative_unit == prefecture

    def test_update_locality(self, locality, user):
        """Test updating a locality."""
        updated = LocalityService.update(
            locality=locality,
            name="Filima Village",
            user=user,
        )
        assert updated.name == "Filima Village"

    def test_delete_locality_with_schools(self, locality, user):
        """Test that cannot delete locality with schools."""
        # Note: This will pass until School model is implemented
        # When School is implemented, this should raise ValidationError
        LocalityService.delete(locality=locality, user=user)
        assert locality.is_deleted is True

    def test_soft_delete_locality(self, locality, user):
        """Test soft deleting a locality."""
        LocalityService.delete(locality=locality, user=user)
        assert locality.is_deleted is True

    def test_restore_locality(self, locality, user):
        """Test restoring a soft-deleted locality."""
        locality.soft_delete(user=user)
        restored = LocalityService.restore(locality=locality, user=user)
        assert restored.is_deleted is False
