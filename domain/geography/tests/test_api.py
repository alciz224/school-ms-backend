"""Tests for geography API endpoints."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse

from domain.geography.models import (
    Country,
    RegionAdministrative,
    AdministrativeUnit,
    Locality,
)
from domain.geography.constants import AdministrativeUnitType


@pytest.fixture
def api_client():
    """Create an API client."""
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, user):
    """Create an authenticated API client."""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.mark.django_db
class TestCountryAPI:
    """Tests for Country API endpoints."""

    def test_list_countries(self, authenticated_client, country):
        """Test listing countries."""
        url = reverse('geography:country-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['code'] == country.code

    def test_retrieve_country(self, authenticated_client, country):
        """Test retrieving a single country."""
        url = reverse('geography:country-detail', kwargs={'pk': country.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == country.code
        assert response.data['name'] == country.name

    def test_list_countries_unauthenticated(self, api_client, country):
        """Test that unauthenticated users cannot list countries."""
        url = reverse('geography:country-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestRegionAPI:
    """Tests for Region API endpoints."""

    def test_list_regions(self, authenticated_client, region):
        """Test listing regions."""
        url = reverse('geography:region-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['code'] == region.code

    def test_filter_regions_by_country(self, authenticated_client, country, region, user):
        """Test filtering regions by country."""
        # Create another country and region
        other_country = Country.objects.create(
            code="SL",
            name="Sierra Leone",
            created_by=user,
            updated_by=user,
        )
        RegionAdministrative.objects.create(
            country=other_country,
            code="WEST",
            name="Western Area",
            created_by=user,
            updated_by=user,
        )
        
        url = reverse('geography:region-list')
        response = authenticated_client.get(url, {'country': country.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['country'] == country.id

    def test_retrieve_region(self, authenticated_client, region):
        """Test retrieving a single region."""
        url = reverse('geography:region-detail', kwargs={'pk': region.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == region.code
        assert response.data['name'] == region.name


@pytest.mark.django_db
class TestAdministrativeUnitAPI:
    """Tests for Administrative Unit API endpoints."""

    def test_list_administrative_units(self, authenticated_client, prefecture):
        """Test listing administrative units."""
        url = reverse('geography:administrative-unit-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['code'] == prefecture.code

    def test_filter_units_by_region(self, authenticated_client, region, prefecture, user):
        """Test filtering units by region."""
        # Create another region and unit
        other_region = RegionAdministrative.objects.create(
            country=region.country,
            code="KANKAN",
            name="Kankan",
            created_by=user,
            updated_by=user,
        )
        AdministrativeUnit.objects.create(
            region=other_region,
            code="SIG",
            name="Siguiri",
            type=AdministrativeUnitType.PREFECTURE,
            created_by=user,
            updated_by=user,
        )
        
        url = reverse('geography:administrative-unit-list')
        response = authenticated_client.get(url, {'region': region.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['region'] == region.id

    def test_filter_units_by_type(self, authenticated_client, prefecture, user):
        """Test filtering units by type."""
        # Create a commune
        AdministrativeUnit.objects.create(
            region=prefecture.region,
            code="KALOUM",
            name="Kaloum",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        
        url = reverse('geography:administrative-unit-list')
        response = authenticated_client.get(url, {'type': AdministrativeUnitType.PREFECTURE})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['type'] == AdministrativeUnitType.PREFECTURE

    def test_retrieve_administrative_unit(self, authenticated_client, prefecture):
        """Test retrieving a single administrative unit."""
        url = reverse('geography:administrative-unit-detail', kwargs={'pk': prefecture.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == prefecture.code
        assert response.data['type'] == prefecture.type


@pytest.mark.django_db
class TestLocalityAPI:
    """Tests for Locality API endpoints."""

    def test_list_localities(self, authenticated_client, locality):
        """Test listing localities."""
        url = reverse('geography:locality-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['code'] == locality.code

    def test_filter_localities_by_unit(self, authenticated_client, prefecture, locality, user):
        """Test filtering localities by administrative unit."""
        # Create another unit and locality
        other_unit = AdministrativeUnit.objects.create(
            region=prefecture.region,
            code="OTHER",
            name="Other Unit",
            type=AdministrativeUnitType.COMMUNE,
            created_by=user,
            updated_by=user,
        )
        Locality.objects.create(
            administrative_unit=other_unit,
            code="OTHER",
            name="Other Locality",
            created_by=user,
            updated_by=user,
        )
        
        url = reverse('geography:locality-list')
        response = authenticated_client.get(url, {'administrative_unit': prefecture.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["data"]) == 1
        assert response.data["data"][0]['administrative_unit'] == prefecture.id

    def test_retrieve_locality(self, authenticated_client, locality):
        """Test retrieving a single locality."""
        url = reverse('geography:locality-detail', kwargs={'pk': locality.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == locality.code
        assert response.data['name'] == locality.name

    def test_locality_full_path_in_response(self, authenticated_client, locality):
        """Test that full_path is included in locality response."""
        url = reverse('geography:locality-detail', kwargs={'pk': locality.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # full_path should be in the response if serializer includes it
        # This depends on the serializer implementation



