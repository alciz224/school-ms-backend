"""Tests for geography selectors."""
import pytest

from domain.geography.selectors import (
    CountrySelector,
    RegionSelector,
    AdministrativeUnitSelector,
    LocalitySelector,
)
from domain.geography.models import RegionAdministrative, AdministrativeUnit, Locality
from domain.geography.constants import AdministrativeUnitType


@pytest.mark.django_db
class TestCountrySelector:
    """Tests for CountrySelector."""

    def test_list_countries(self, country):
        """Test listing all countries."""
        countries = CountrySelector.list()
        assert countries.count() == 1
        assert country in countries

    def test_get_by_id(self, country):
        """Test getting country by ID."""
        result = CountrySelector.get_by_id(country_id=country.id)
        assert result == country

    def test_get_by_code(self, country):
        """Test getting country by code."""
        result = CountrySelector.get_by_code(code="GN")
        assert result == country
        
        # Test case insensitive
        result = CountrySelector.get_by_code(code="gn")
        assert result == country

    def test_get_by_name(self, country):
        """Test getting country by name."""
        result = CountrySelector.get_by_name(name="Guinea")
        assert result == country


@pytest.mark.django_db
class TestRegionSelector:
    """Tests for RegionSelector."""

    def test_list_regions(self, region):
        """Test listing all regions."""
        regions = RegionSelector.list()
        assert regions.count() == 1
        assert region in regions

    def test_list_by_country(self, country, region, user):
        """Test listing regions by country."""
        # Create another region
        RegionAdministrative.objects.create(
            country=country,
            code="KANKAN",
            name="Kankan",
            created_by=user,
            updated_by=user,
        )
        
        regions = RegionSelector.list(country_id=country.id)
        assert regions.count() == 2

    def test_get_by_id(self, region):
        """Test getting region by ID."""
        result = RegionSelector.get_by_id(region_id=region.id)
        assert result == region

    def test_get_by_code(self, region):
        """Test getting region by code."""
        result = RegionSelector.get_by_code(
            country_id=region.country_id,
            code="BOKE"
        )
        assert result == region


@pytest.mark.django_db
class TestAdministrativeUnitSelector:
    """Tests for AdministrativeUnitSelector."""

    def test_list_units(self, prefecture):
        """Test listing all administrative units."""
        units = AdministrativeUnitSelector.list()
        assert units.count() == 1
        assert prefecture in units

    def test_list_by_region(self, region, prefecture, user):
        """Test listing units by region."""
        # Create another unit
        AdministrativeUnit.objects.create(
            region=region,
            code="KALOUM",
            name="Kaloum",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        
        units = AdministrativeUnitSelector.list(region_id=region.id)
        assert units.count() == 2

    def test_list_by_type(self, prefecture, user):
        """Test listing units by type."""
        # Create a commune
        AdministrativeUnit.objects.create(
            region=prefecture.region,
            code="KALOUM",
            name="Kaloum",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        
        prefectures = AdministrativeUnitSelector.list(
            unit_type=AdministrativeUnitType.PREFECTURE
        )
        assert prefectures.count() == 1
        assert prefecture in prefectures

    def test_get_by_id(self, prefecture):
        """Test getting unit by ID."""
        result = AdministrativeUnitSelector.get_by_id(unit_id=prefecture.id)
        assert result == prefecture

    def test_get_prefectures(self, prefecture, user):
        """Test getting only prefectures."""
        # Create a commune
        AdministrativeUnit.objects.create(
            region=prefecture.region,
            code="KALOUM",
            name="Kaloum",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        
        prefectures = AdministrativeUnitSelector.get_prefectures()
        assert prefectures.count() == 1
        assert prefecture in prefectures

    def test_get_communes(self, prefecture, user):
        """Test getting only communes."""
        commune = AdministrativeUnit.objects.create(
            region=prefecture.region,
            code="KALOUM",
            name="Kaloum",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        
        communes = AdministrativeUnitSelector.get_communes()
        assert communes.count() == 1
        assert commune in communes

    def test_get_children(self, prefecture, subprefecture):
        """Test getting child units."""
        children = AdministrativeUnitSelector.get_children(parent_id=prefecture.id)
        assert children.count() == 1
        assert subprefecture in children


@pytest.mark.django_db
class TestLocalitySelector:
    """Tests for LocalitySelector."""

    def test_list_localities(self, locality):
        """Test listing all localities."""
        localities = LocalitySelector.list()
        assert localities.count() == 1
        assert locality in localities

    def test_list_by_administrative_unit(self, prefecture, locality, user):
        """Test listing localities by administrative unit."""
        # Create another locality
        Locality.objects.create(
            administrative_unit=prefecture,
            code="VILLAGE2",
            name="Village 2",
            created_by=user,
            updated_by=user,
        )
        
        localities = LocalitySelector.list(administrative_unit_id=prefecture.id)
        assert localities.count() == 2

    def test_get_by_id(self, locality):
        """Test getting locality by ID."""
        result = LocalitySelector.get_by_id(locality_id=locality.id)
        assert result == locality

    def test_get_by_code(self, locality):
        """Test getting locality by code."""
        result = LocalitySelector.get_by_code(
            administrative_unit_id=locality.administrative_unit_id,
            code="FILIMA"
        )
        assert result == locality

    def test_filter_by_region(self, region, locality, user):
        """Test filtering localities by region."""
        # Create another region and locality
        other_region = RegionAdministrative.objects.create(
            country=region.country,
            code="KANKAN",
            name="Kankan",
            created_by=user,
            updated_by=user,
        )
        other_unit = AdministrativeUnit.objects.create(
            region=other_region,
            code="SIG",
            name="Siguiri",
            type=AdministrativeUnitType.PREFECTURE,
            created_by=user,
            updated_by=user,
        )
        Locality.objects.create(
            administrative_unit=other_unit,
            code="TOWN",
            name="Town",
            created_by=user,
            updated_by=user,
        )
        
        # Should only get localities from Boké region
        localities = LocalitySelector.filter_by_region(region_id=region.id)
        assert localities.count() == 1
        assert locality in localities
