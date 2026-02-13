"""Tests for geography models."""
import pytest
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

from domain.geography.models import (
    Country,
    RegionAdministrative,
    AdministrativeUnit,
    Locality,
)
from domain.geography.constants import AdministrativeUnitType


@pytest.mark.django_db
class TestCountryModel:
    """Tests for Country model."""

    def test_create_country(self, user):
        """Test creating a country."""
        country = Country.objects.create(
            code="GN",
            name="Guinea",
            description="Republic of Guinea",
            created_by=user,
            updated_by=user,
        )
        assert country.id is not None
        assert country.code == "GN"
        assert country.name == "Guinea"
        assert str(country) == "Guinea (GN)"

    def test_country_code_unique(self, country):
        """Test that country code must be unique."""
        with pytest.raises(IntegrityError):
            Country.objects.create(
                code="GN",  # Duplicate
                name="Different Name",
            )

    def test_country_name_unique(self, country):
        """Test that country name must be unique."""
        with pytest.raises(IntegrityError):
            Country.objects.create(
                code="XX",
                name="Guinea",  # Duplicate
            )

    def test_regions_count_property(self, country, region):
        """Test regions_count property."""
        assert country.regions_count == 1
        
        # Add another region
        RegionAdministrative.objects.create(
            country=country,
            code="KANKAN",
            name="Kankan",
        )
        assert country.regions_count == 2

    def test_soft_delete(self, country, user):
        """Test soft delete functionality."""
        country.soft_delete(user=user)
        assert country.is_deleted is True
        assert country.deleted_at is not None
        assert country.deleted_by == user


@pytest.mark.django_db
class TestRegionModel:
    """Tests for RegionAdministrative model."""

    def test_create_region(self, country, user):
        """Test creating a region."""
        region = RegionAdministrative.objects.create(
            country=country,
            code="BOKE",
            name="Boké",
            created_by=user,
            updated_by=user,
        )
        assert region.id is not None
        assert region.country == country
        assert str(region) == "Boké (BOKE)"

    def test_region_code_unique_per_country(self, country, region):
        """Test that region code must be unique per country."""
        with pytest.raises(IntegrityError):
            RegionAdministrative.objects.create(
                country=country,
                code="BOKE",  # Duplicate in same country
                name="Different Name",
            )

    def test_region_name_unique_per_country(self, country, region):
        """Test that region name must be unique per country."""
        with pytest.raises(IntegrityError):
            RegionAdministrative.objects.create(
                country=country,
                code="DIFFERENT",
                name="Boké",  # Duplicate in same country
            )

    def test_administrative_units_count_property(self, region, prefecture):
        """Test administrative_units_count property."""
        assert region.administrative_units_count == 1


@pytest.mark.django_db
class TestAdministrativeUnitModel:
    """Tests for AdministrativeUnit model."""

    def test_create_prefecture(self, region, user):
        """Test creating a prefecture."""
        prefecture = AdministrativeUnit.objects.create(
            region=region,
            code="KAMSAR",
            name="Kamsar",
            type=AdministrativeUnitType.PREFECTURE,
            created_by=user,
            updated_by=user,
        )
        assert prefecture.id is not None
        assert prefecture.parent is None
        assert str(prefecture) == "Kamsar (Prefecture)"

    def test_create_commune(self, region, user):
        """Test creating a commune."""
        commune = AdministrativeUnit.objects.create(
            region=region,
            code="KALOUM",
            name="Kaloum",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        assert commune.id is not None
        assert commune.parent is None

    def test_create_subprefecture(self, prefecture, user):
        """Test creating a subprefecture."""
        subprefecture = AdministrativeUnit.objects.create(
            region=prefecture.region,
            parent=prefecture,
            code="KASSAPO",
            name="Kassapo",
            type=AdministrativeUnitType.SUBPREFECTURE,
            created_by=user,
            updated_by=user,
        )
        assert subprefecture.id is not None
        assert subprefecture.parent == prefecture

    def test_subprefecture_requires_parent(self, region):
        """Test that subprefecture must have a parent."""
        with pytest.raises(ValidationError) as exc_info:
            unit = AdministrativeUnit(
                region=region,
                code="TEST",
                name="Test",
                type=AdministrativeUnitType.SUBPREFECTURE,
                parent=None,  # Missing parent
            )
            unit.save()
        assert 'parent' in exc_info.value.message_dict

    def test_prefecture_cannot_have_parent(self, region, prefecture):
        """Test that prefecture cannot have a parent."""
        with pytest.raises(ValidationError) as exc_info:
            unit = AdministrativeUnit(
                region=region,
                parent=prefecture,  # Should not have parent
                code="TEST",
                name="Test",
                type=AdministrativeUnitType.PREFECTURE,
            )
            unit.save()
        assert 'parent' in exc_info.value.message_dict

    def test_subprefecture_parent_must_be_prefecture(self, region, user):
        """Test that subprefecture parent must be a prefecture."""
        commune = AdministrativeUnit.objects.create(
            region=region,
            code="COMMUNE1",
            name="Commune 1",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            unit = AdministrativeUnit(
                region=region,
                parent=commune,  # Parent is commune, not prefecture
                code="TEST",
                name="Test",
                type=AdministrativeUnitType.SUBPREFECTURE,
            )
            unit.save()
        assert 'parent' in exc_info.value.message_dict

    def test_parent_must_be_same_region(self, region, prefecture, user):
        """Test that parent must be in same region."""
        # Create another region
        other_region = RegionAdministrative.objects.create(
            country=region.country,
            code="OTHER",
            name="Other Region",
            created_by=user,
            updated_by=user,
        )
        
        with pytest.raises(ValidationError) as exc_info:
            unit = AdministrativeUnit(
                region=other_region,  # Different region
                parent=prefecture,
                code="TEST",
                name="Test",
                type=AdministrativeUnitType.SUBPREFECTURE,
            )
            unit.save()
        assert 'parent' in exc_info.value.message_dict

    def test_localities_count_property(self, prefecture, locality):
        """Test localities_count property."""
        assert prefecture.localities_count == 1

    def test_children_count_property(self, prefecture, subprefecture):
        """Test children_count property."""
        assert prefecture.children_count == 1


@pytest.mark.django_db
class TestLocalityModel:
    """Tests for Locality model."""

    def test_create_locality(self, prefecture, user):
        """Test creating a locality."""
        locality = Locality.objects.create(
            administrative_unit=prefecture,
            code="FILIMA",
            name="Filima",
            created_by=user,
            updated_by=user,
        )
        assert locality.id is not None
        assert locality.administrative_unit == prefecture
        assert str(locality) == "Filima"

    def test_locality_code_unique_per_unit(self, prefecture, locality):
        """Test that locality code must be unique per administrative unit."""
        with pytest.raises(IntegrityError):
            Locality.objects.create(
                administrative_unit=prefecture,
                code="FILIMA",  # Duplicate in same unit
                name="Different Name",
            )

    def test_locality_name_unique_per_unit(self, prefecture, locality):
        """Test that locality name must be unique per administrative unit."""
        with pytest.raises(IntegrityError):
            Locality.objects.create(
                administrative_unit=prefecture,
                code="DIFFERENT",
                name="Filima",  # Duplicate in same unit
            )

    def test_full_path_property(self, locality, prefecture):
        """Test full_path property."""
        path = locality.full_path
        assert "Guinea" in path
        assert "Boké" in path
        assert "Kamsar" in path
        assert "Filima" in path
        assert " > " in path

    def test_full_path_with_subprefecture(self, subprefecture, user):
        """Test full_path includes parent for subprefecture locality."""
        locality = Locality.objects.create(
            administrative_unit=subprefecture,
            code="VILLAGE1",
            name="Village 1",
            created_by=user,
            updated_by=user,
        )
        path = locality.full_path
        # Should include: Country > Region > Prefecture > Subprefecture > Locality
        assert "Guinea" in path
        assert "Boké" in path
        assert "Kamsar" in path  # Parent prefecture
        assert "Kassapo" in path  # Subprefecture
        assert "Village 1" in path
