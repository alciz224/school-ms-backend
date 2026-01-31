"""
Tests for SchoolYear model.
"""

import pytest
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from domain.school_operations.models import School, SchoolYear
from domain.school_operations.constants import SchoolYearStatus, SchoolStatus, SchoolType, SchoolOwnership
from domain.academic.models import AcademicYear
from domain.academic.constants import AcademicYearStatus
from domain.geography.models import Country, RegionAdministrative, AdministrativeUnit, Locality
from domain.geography.constants import AdministrativeUnitType


@pytest.fixture
def guinea_geography(db):
    """Create Guinea geography structure."""
    country = Country.objects.create(
        code='GN',
        name='Guinea'
    )
    
    region = RegionAdministrative.objects.create(
        country=country,
        code='BOK',
        name='Boké'
    )
    
    admin_unit = AdministrativeUnit.objects.create(
        region=region,
        code='BOK-C',
        name='Boké Centre',
        type=AdministrativeUnitType.PREFECTURE
    )
    
    locality = Locality.objects.create(
        administrative_unit=admin_unit,
        code='FILIMA',
        name='Filima'
    )
    
    return {
        'country': country,
        'region': region,
        'admin_unit': admin_unit,
        'locality': locality
    }


@pytest.fixture
def school(db, guinea_geography):
    """Create a test school."""
    return School.objects.create(
        name='Lycée Filima',
        code='LYC-FILIMA-001',
        school_type=SchoolType.LYCEE,
        ownership=SchoolOwnership.PUBLIC,
        status=SchoolStatus.ACTIVE,
        locality=guinea_geography['locality'],
        capacity=500,
        address='Filima, Boké'
    )


@pytest.fixture
def academic_year(db):
    """Create a test academic year."""
    return AcademicYear.objects.create(
        start_year=2024,
        end_year=2025,
        status=AcademicYearStatus.ACTIVE,
        is_current=True
    )


@pytest.fixture
def school_year(db, school, academic_year):
    """Create a test school year."""
    return SchoolYear.objects.create(
        school=school,
        academic_year=academic_year,
        name=f"{school.name} {academic_year.code}",
        start_date=date(2024, 10, 1),
        end_date=date(2025, 6, 30),
        enrollment_start_date=date(2024, 9, 1),
        enrollment_end_date=date(2024, 9, 30),
        capacity=500,
        status=SchoolYearStatus.PLANNING
    )


@pytest.mark.django_db
class TestSchoolYearModel:
    """Test SchoolYear model."""
    
    def test_create_school_year(self, school, academic_year):
        """Test creating a school year."""
        school_year = SchoolYear.objects.create(
            school=school,
            academic_year=academic_year,
            name=f"{school.name} {academic_year.code}",
            start_date=date(2024, 10, 1),
            end_date=date(2025, 6, 30),
            capacity=500
        )
        
        assert school_year.id is not None
        assert school_year.school == school
        assert school_year.academic_year == academic_year
        assert school_year.status == SchoolYearStatus.PLANNING
        assert school_year.is_current is False
        assert school_year.current_enrollment_count == 0
    
    def test_code_auto_generation(self, school_year):
        """Test that code is auto-generated."""
        assert school_year.code == 'LYC-FILIMA-001-2024-2025'
    
    def test_name_generation(self, school, academic_year):
        """Test name generation."""
        school_year = SchoolYear.objects.create(
            school=school,
            academic_year=academic_year,
            name=f"{school.name} {academic_year.code}",
            start_date=date(2024, 10, 1),
            end_date=date(2025, 6, 30)
        )
        
        assert school_year.name == 'Lycée Filima 2024-2025'
    
    def test_unique_school_academic_year(self, school, academic_year, school_year):
        """Test uniqueness of school + academic year combination."""
        with pytest.raises((IntegrityError, ValidationError)):
            SchoolYear.objects.create(
                school=school,
                academic_year=academic_year,
                name='Duplicate',
                start_date=date(2024, 11, 1),  # Different dates to avoid date constraint
                end_date=date(2025, 7, 30)
            )
    
    def test_unique_current_per_school(self, school, academic_year, school_year):
        """Test only one current year per school."""
        school_year.is_current = True
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        # Create another year for same school
        academic_year_2 = AcademicYear.objects.create(
            start_year=2025,
            end_year=2026,
            status=AcademicYearStatus.ACTIVE
        )
        
        school_year_2 = SchoolYear.objects.create(
            school=school,
            academic_year=academic_year_2,
            name=f"{school.name} {academic_year_2.code}",
            start_date=date(2025, 10, 1),
            end_date=date(2026, 6, 30),
            status=SchoolYearStatus.ACTIVE,
            is_current=True
        )
        
        # First should be un-set
        school_year.refresh_from_db()
        assert school_year.is_current is False
        assert school_year_2.is_current is True
    
    def test_unique_active_per_school(self, school, academic_year, school_year):
        """Test only one active year per school."""
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        # Create another year for same school
        academic_year_2 = AcademicYear.objects.create(
            start_year=2025,
            end_year=2026,
            status=AcademicYearStatus.ACTIVE
        )
        
        school_year_2 = SchoolYear.objects.create(
            school=school,
            academic_year=academic_year_2,
            name=f"{school.name} {academic_year_2.code}",
            start_date=date(2025, 10, 1),
            end_date=date(2026, 6, 30),
            status=SchoolYearStatus.ACTIVE
        )
        
        # First should be changed to planning
        school_year.refresh_from_db()
        assert school_year.status == SchoolYearStatus.PLANNING
        assert school_year_2.status == SchoolYearStatus.ACTIVE
    
    def test_date_validation(self, school, academic_year):
        """Test date validation."""
        with pytest.raises(ValidationError):
            school_year = SchoolYear(
                school=school,
                academic_year=academic_year,
                name='Test',
                start_date=date(2024, 10, 1),
                end_date=date(2024, 9, 1)  # End before start
            )
            school_year.full_clean()
    
    def test_enrollment_period_validation(self, school, academic_year):
        """Test enrollment period validation."""
        with pytest.raises(ValidationError):
            school_year = SchoolYear(
                school=school,
                academic_year=academic_year,
                name='Test',
                start_date=date(2024, 10, 1),
                end_date=date(2025, 6, 30),
                enrollment_start_date=date(2024, 9, 1),
                enrollment_end_date=date(2024, 8, 1)  # End before start
            )
            school_year.full_clean()
    
    def test_enrollment_after_year_start_validation(self, school, academic_year):
        """Test that enrollment can't end after year starts."""
        with pytest.raises(ValidationError):
            school_year = SchoolYear(
                school=school,
                academic_year=academic_year,
                name='Test',
                start_date=date(2024, 10, 1),
                end_date=date(2025, 6, 30),
                enrollment_start_date=date(2024, 9, 1),
                enrollment_end_date=date(2024, 11, 1)  # After year start
            )
            school_year.full_clean()
    
    def test_capacity_exceeds_school_capacity(self, school, academic_year):
        """Test that school year capacity can't exceed school capacity."""
        with pytest.raises(ValidationError):
            school_year = SchoolYear(
                school=school,
                academic_year=academic_year,
                name='Test',
                start_date=date(2024, 10, 1),
                end_date=date(2025, 6, 30),
                capacity=1000  # School capacity is 500
            )
            school_year.full_clean()
    
    def test_archived_cannot_be_current(self, school_year):
        """Test that archived years cannot be current."""
        school_year.status = SchoolYearStatus.ARCHIVED
        school_year.is_current = True
        
        with pytest.raises(ValidationError):
            school_year.full_clean()
    
    def test_current_must_be_active(self, school_year):
        """Test that current year must be active."""
        school_year.status = SchoolYearStatus.PLANNING
        school_year.is_current = True
        
        with pytest.raises(ValidationError):
            school_year.full_clean()


@pytest.mark.django_db
class TestSchoolYearMethods:
    """Test SchoolYear methods."""
    
    def test_is_enrollment_open(self, school_year):
        """Test is_enrollment_open method."""
        # Set enrollment period around today, but before year start
        today = date.today()
        school_year.enrollment_start_date = today - timedelta(days=5)
        school_year.enrollment_end_date = today + timedelta(days=5)
        school_year.start_date = today + timedelta(days=10)  # Start after enrollment
        school_year.end_date = today + timedelta(days=280)
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        assert school_year.is_enrollment_open() is True
    
    def test_is_enrollment_closed(self, school_year):
        """Test enrollment is closed when outside period."""
        school_year.enrollment_start_date = date(2024, 9, 1)
        school_year.enrollment_end_date = date(2024, 9, 30)
        school_year.save()
        
        # Assuming today is not in September 2024
        assert school_year.is_enrollment_open() is False
    
    def test_has_capacity(self, school_year):
        """Test has_capacity method."""
        school_year.capacity = 100
        school_year.current_enrollment_count = 50
        school_year.save()
        
        assert school_year.has_capacity() is True
    
    def test_no_capacity_when_full(self, school_year):
        """Test no capacity when full."""
        school_year.capacity = 100
        school_year.current_enrollment_count = 100
        school_year.save()
        
        assert school_year.has_capacity() is False
    
    def test_available_capacity(self, school_year):
        """Test available_capacity method."""
        school_year.capacity = 100
        school_year.current_enrollment_count = 30
        school_year.save()
        
        assert school_year.available_capacity() == 70
    
    def test_available_capacity_unlimited(self, school_year):
        """Test available capacity when no limit set."""
        school_year.capacity = None
        school_year.save()
        
        assert school_year.available_capacity() is None
    
    def test_activate(self, school_year):
        """Test activate method."""
        school_year.activate()
        
        assert school_year.status == SchoolYearStatus.ACTIVE
        assert school_year.is_current is True
    
    def test_complete(self, school_year):
        """Test complete method."""
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.is_current = True
        school_year.save()
        
        school_year.complete()
        
        assert school_year.status == SchoolYearStatus.COMPLETED
        assert school_year.is_current is False
    
    def test_archive(self, school_year):
        """Test archive method."""
        school_year.status = SchoolYearStatus.COMPLETED
        school_year.save()
        
        school_year.archive()
        
        assert school_year.status == SchoolYearStatus.ARCHIVED
        assert school_year.is_current is False
    
    def test_cannot_archive_active(self, school_year):
        """Test cannot archive active year."""
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        with pytest.raises(ValidationError):
            school_year.archive()
    
    def test_get_setting(self, school_year):
        """Test get_setting method."""
        school_year.settings = {
            'assessment': {
                'passing_grade': 10.0
            }
        }
        school_year.save()
        
        assert school_year.get_setting('assessment.passing_grade') == 10.0
        assert school_year.get_setting('assessment.nonexistent', 'default') == 'default'
    
    def test_update_setting(self, school_year):
        """Test update_setting method."""
        school_year.settings = {}
        school_year.save()
        
        school_year.update_setting('assessment.passing_grade', 12.0)
        
        assert school_year.settings['assessment']['passing_grade'] == 12.0
    
    def test_add_holiday(self, school_year):
        """Test add_holiday method."""
        school_year.settings = {'holidays': []}
        school_year.save()
        
        school_year.add_holiday(
            'Christmas Break',
            date(2024, 12, 20),
            date(2025, 1, 5)
        )
        
        assert len(school_year.settings['holidays']) == 1
        assert school_year.settings['holidays'][0]['name'] == 'Christmas Break'
    
    def test_increment_enrollment_count(self, school_year):
        """Test increment_enrollment_count method."""
        initial_count = school_year.current_enrollment_count
        school_year.increment_enrollment_count(5)
        
        assert school_year.current_enrollment_count == initial_count + 5
    
    def test_decrement_enrollment_count(self, school_year):
        """Test decrement_enrollment_count method."""
        school_year.current_enrollment_count = 10
        school_year.save()
        
        school_year.decrement_enrollment_count(3)
        
        assert school_year.current_enrollment_count == 7
    
    def test_can_be_deleted(self, school_year):
        """Test can_be_deleted method."""
        can_delete, reason = school_year.can_be_deleted()
        assert can_delete is True
    
    def test_cannot_delete_active(self, school_year):
        """Test cannot delete active year."""
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        can_delete, reason = school_year.can_be_deleted()
        assert can_delete is False
    
    def test_cannot_delete_current(self, school_year):
        """Test cannot delete current year."""
        school_year.is_current = True
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        can_delete, reason = school_year.can_be_deleted()
        assert can_delete is False


@pytest.mark.django_db
class TestSchoolYearManager:
    """Test SchoolYear manager methods."""
    
    def test_get_current_for_school(self, school, school_year):
        """Test get_current_for_school method."""
        school_year.is_current = True
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        current = SchoolYear.objects.get_current_for_school(school)
        
        assert current == school_year
    
    def test_get_active_for_school(self, school, school_year):
        """Test get_active_for_school method."""
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        active = SchoolYear.objects.get_active_for_school(school)
        
        assert active == school_year
    
    def test_get_by_academic_year(self, academic_year, school_year):
        """Test get_by_academic_year method."""
        results = SchoolYear.objects.get_by_academic_year(academic_year)
        
        assert school_year in results
    
    def test_get_planning(self, school_year):
        """Test get_planning method."""
        results = SchoolYear.objects.get_planning()
        
        assert school_year in results
    
    def test_get_active(self, school_year):
        """Test get_active method."""
        school_year.status = SchoolYearStatus.ACTIVE
        school_year.save()
        
        results = SchoolYear.objects.get_active()
        
        assert school_year in results


@pytest.mark.django_db
class TestSchoolYearDefaults:
    """Test SchoolYear default settings."""
    
    def test_get_default_settings(self, school_year):
        """Test get_default_settings method."""
        defaults = school_year.get_default_settings()
        
        assert 'grading_periods' in defaults
        assert 'holidays' in defaults
        assert 'attendance' in defaults
        assert 'assessment' in defaults
        assert 'calendar' in defaults
        assert 'policies' in defaults
        assert defaults['assessment']['grading_scale'] == '20_point'
        assert defaults['assessment']['passing_grade'] == 10.0
