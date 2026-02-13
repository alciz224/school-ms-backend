"""Tests for academic API endpoints."""
import pytest
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse


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
class TestAcademicYearAPI:
    """Tests for AcademicYear API endpoints."""

    def test_list_academic_years(self, authenticated_client, academic_year):
        """Test listing academic years."""
        url = reverse('academic:academicyear-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_academic_year(self, authenticated_client, academic_year):
        """Test retrieving a single academic year."""
        url = reverse('academic:academicyear-detail', kwargs={'pk': academic_year.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == academic_year.code

    def test_list_requires_authentication(self, api_client):
        """Test that authentication is required."""
        url = reverse('academic:academicyear-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestCycleAPI:
    """Tests for Cycle API endpoints."""

    def test_list_cycles(self, authenticated_client, cycle):
        """Test listing cycles."""
        url = reverse('academic:cycle-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_cycle(self, authenticated_client, cycle):
        """Test retrieving a single cycle."""
        url = reverse('academic:cycle-detail', kwargs={'pk': cycle.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == cycle.code


@pytest.mark.django_db
class TestTrackAPI:
    """Tests for Track API endpoints."""

    def test_list_tracks(self, authenticated_client, track):
        """Test listing tracks."""
        url = reverse('academic:track-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_tracks_by_cycle(self, authenticated_client, track):
        """Test filtering tracks by cycle."""
        url = reverse('academic:track-list')
        response = authenticated_client.get(url, {'cycle': track.cycle.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['cycle'] == track.cycle.id


@pytest.mark.django_db
class TestLevelAPI:
    """Tests for Level API endpoints."""

    def test_list_levels(self, authenticated_client, level):
        """Test listing levels."""
        url = reverse('academic:level-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_levels_by_cycle(self, authenticated_client, level):
        """Test filtering levels by cycle."""
        url = reverse('academic:level-list')
        response = authenticated_client.get(url, {'cycle': level.cycle.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_levels_by_track(self, authenticated_client, cycle_with_track, track, user):
        """Test filtering levels by track."""
        from domain.academic.models import Level
        level = Level.objects.create(
            cycle=cycle_with_track,
            track=track,
            code="TS",
            name="Terminale S",
            order=1,
            created_by=user,
            updated_by=user,
        )
        
        url = reverse('academic:level-list')
        response = authenticated_client.get(url, {'track': track.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1


@pytest.mark.django_db
class TestSubjectAPI:
    """Tests for Subject API endpoints."""

    def test_list_subjects(self, authenticated_client, subject):
        """Test listing subjects."""
        url = reverse('academic:subject-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_subject(self, authenticated_client, subject):
        """Test retrieving a single subject."""
        url = reverse('academic:subject-detail', kwargs={'pk': subject.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == subject.code


@pytest.mark.django_db
class TestAssessmentTypeAPI:
    """Tests for AssessmentType API endpoints."""

    def test_list_assessment_types(self, authenticated_client, assessment_type):
        """Test listing assessment types."""
        url = reverse('academic:assessmenttype-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_assessment_type(self, authenticated_client, assessment_type):
        """Test retrieving a single assessment type."""
        url = reverse('academic:assessmenttype-detail', kwargs={'pk': assessment_type.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == assessment_type.code


@pytest.mark.django_db
class TestTermTypeAPI:
    """Tests for TermType API endpoints."""

    def test_list_term_types(self, authenticated_client, term_type):
        """Test listing term types."""
        url = reverse('academic:termtype-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_retrieve_term_type(self, authenticated_client, term_type):
        """Test retrieving a single term type."""
        url = reverse('academic:termtype-detail', kwargs={'pk': term_type.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == term_type.code


@pytest.mark.django_db
class TestTermAPI:
    """Tests for Term API endpoints."""

    def test_list_terms(self, authenticated_client, term):
        """Test listing terms."""
        url = reverse('academic:term-list')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_filter_terms_by_term_type(self, authenticated_client, term):
        """Test filtering terms by term type."""
        url = reverse('academic:term-list')
        response = authenticated_client.get(url, {'term_type': term.term_type.id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['term_type'] == term.term_type.id

    def test_retrieve_term(self, authenticated_client, term):
        """Test retrieving a single term."""
        url = reverse('academic:term-detail', kwargs={'pk': term.id})
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['code'] == term.code
