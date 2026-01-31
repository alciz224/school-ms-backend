"""Tests for SchoolYearCycle model, services, and selectors."""
import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone

from domain.academic.models import Cycle, TermType
from domain.school_operations.models import SchoolYear, SchoolYearCycle
from domain.school_operations.selectors.school_year_cycle import SchoolYearCycleSelector
from domain.school_operations.services.school_year_cycle import SchoolYearCycleService


@pytest.fixture
def cycle(db):
    """Create a test cycle."""
    return Cycle.objects.create(
        code="PRI",
        name="Primaire",
        has_track=False,
    )


@pytest.fixture
def cycle_with_track(db):
    """Create a test cycle with track."""
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




@pytest.mark.django_db
class TestSchoolYearCycleModel:
    """Test SchoolYearCycle model."""

    def test_create_school_year_cycle(self, school_year, cycle, term_type_trimester):
        """Test creating a school year cycle."""
        school_year_cycle = SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        assert school_year_cycle.id is not None
        assert school_year_cycle.school_year == school_year
        assert school_year_cycle.cycle == cycle
        assert school_year_cycle.term_type == term_type_trimester
        assert school_year_cycle.is_deleted is False

    def test_school_year_cycle_str(self, school_year, cycle, term_type_trimester):
        """Test __str__ method."""
        school_year_cycle = SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        expected = f"{school_year} - {cycle} ({term_type_trimester})"
        assert str(school_year_cycle) == expected

    def test_unique_constraint_school_year_cycle(
        self, school_year, cycle, term_type_trimester
    ):
        """Test unique constraint on (school_year, cycle)."""
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        # Should raise error when trying to create duplicate
        with pytest.raises(Exception):  # IntegrityError
            SchoolYearCycle.objects.create(
                school_year=school_year,
                cycle=cycle,
                term_type=term_type_trimester,
            )

    def test_can_delete(self, school_year, cycle, term_type_trimester):
        """Test can_delete method."""
        school_year_cycle = SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        # Should be able to delete when no dependencies
        assert school_year_cycle.can_delete() is True


@pytest.mark.django_db
class TestSchoolYearCycleService:
    """Test SchoolYearCycleService."""

    def test_create_school_year_cycle(
        self, school_year, cycle, term_type_trimester, user
    ):
        """Test creating a school year cycle via service."""
        school_year_cycle = SchoolYearCycleService.create(
            school_year_id=school_year.id,
            cycle_id=cycle.id,
            term_type_id=term_type_trimester.id,
            created_by=user,
        )

        assert school_year_cycle.id is not None
        assert school_year_cycle.school_year_id == school_year.id
        assert school_year_cycle.cycle_id == cycle.id
        assert school_year_cycle.term_type_id == term_type_trimester.id
        assert school_year_cycle.created_by == user
        assert school_year_cycle.updated_by == user

    def test_create_duplicate_raises_error(
        self, school_year, cycle, term_type_trimester, user
    ):
        """Test creating duplicate raises error."""
        SchoolYearCycleService.create(
            school_year_id=school_year.id,
            cycle_id=cycle.id,
            term_type_id=term_type_trimester.id,
            created_by=user,
        )

        # Should raise error on duplicate
        with pytest.raises(Exception):  # IntegrityError
            SchoolYearCycleService.create(
                school_year_id=school_year.id,
                cycle_id=cycle.id,
                term_type_id=term_type_trimester.id,
                created_by=user,
            )

    def test_update_school_year_cycle(
        self, school_year, cycle, term_type_trimester, term_type_semester, user
    ):
        """Test updating a school year cycle."""
        school_year_cycle = SchoolYearCycleService.create(
            school_year_id=school_year.id,
            cycle_id=cycle.id,
            term_type_id=term_type_trimester.id,
            created_by=user,
        )

        # Update term type
        updated = SchoolYearCycleService.update(
            school_year_cycle=school_year_cycle,
            term_type_id=term_type_semester.id,
            updated_by=user,
        )

        assert updated.term_type_id == term_type_semester.id
        assert updated.updated_by == user

    def test_delete_school_year_cycle(
        self, school_year, cycle, term_type_trimester, user
    ):
        """Test soft deleting a school year cycle."""
        school_year_cycle = SchoolYearCycleService.create(
            school_year_id=school_year.id,
            cycle_id=cycle.id,
            term_type_id=term_type_trimester.id,
            created_by=user,
        )

        deleted = SchoolYearCycleService.delete(
            school_year_cycle=school_year_cycle,
            deleted_by=user,
        )

        assert deleted.is_deleted is True
        assert deleted.deleted_by == user
        assert deleted.deleted_at is not None

    def test_restore_school_year_cycle(
        self, school_year, cycle, term_type_trimester, user
    ):
        """Test restoring a soft-deleted school year cycle."""
        school_year_cycle = SchoolYearCycleService.create(
            school_year_id=school_year.id,
            cycle_id=cycle.id,
            term_type_id=term_type_trimester.id,
            created_by=user,
        )

        # Delete it
        SchoolYearCycleService.delete(
            school_year_cycle=school_year_cycle,
            deleted_by=user,
        )

        # Restore it
        restored = SchoolYearCycleService.restore(
            school_year_cycle=school_year_cycle,
            updated_by=user,
        )

        assert restored.is_deleted is False
        assert restored.deleted_by is None
        assert restored.deleted_at is None

    def test_bulk_create_for_school_year(
        self, school_year, cycle, cycle_with_track, term_type_trimester, term_type_semester, user
    ):
        """Test bulk creating cycle configurations."""
        cycle_configs = [
            {"cycle_id": cycle.id, "term_type_id": term_type_trimester.id},
            {"cycle_id": cycle_with_track.id, "term_type_id": term_type_semester.id},
        ]

        created_cycles = SchoolYearCycleService.bulk_create_for_school_year(
            school_year_id=school_year.id,
            cycle_configs=cycle_configs,
            created_by=user,
        )

        assert len(created_cycles) == 2
        assert created_cycles[0].cycle_id == cycle.id
        assert created_cycles[1].cycle_id == cycle_with_track.id


@pytest.mark.django_db
class TestSchoolYearCycleSelector:
    """Test SchoolYearCycleSelector."""

    def test_get_by_id(self, school_year, cycle, term_type_trimester):
        """Test getting by ID."""
        school_year_cycle = SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        found = SchoolYearCycleSelector.get_by_id(id=school_year_cycle.id)
        assert found is not None
        assert found.id == school_year_cycle.id

    def test_get_by_school_year_and_cycle(self, school_year, cycle, term_type_trimester):
        """Test getting by school year and cycle."""
        school_year_cycle = SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        found = SchoolYearCycleSelector.get_by_school_year_and_cycle(
            school_year_id=school_year.id,
            cycle_id=cycle.id,
        )

        assert found is not None
        assert found.id == school_year_cycle.id

    def test_list_by_school_year(
        self, school_year, cycle, cycle_with_track, term_type_trimester, term_type_semester
    ):
        """Test listing cycles by school year."""
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle_with_track,
            term_type=term_type_semester,
        )

        cycles = SchoolYearCycleSelector.list_by_school_year(
            school_year_id=school_year.id
        )

        assert cycles.count() == 2

    def test_list_by_school(self, school_year, cycle, term_type_trimester):
        """Test listing cycles by school."""
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        cycles = SchoolYearCycleSelector.list_by_school(
            school_id=school_year.school_id
        )

        assert cycles.count() == 1

    def test_list_by_cycle(self, school_year, cycle, term_type_trimester):
        """Test listing by cycle."""
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        cycles = SchoolYearCycleSelector.list_by_cycle(cycle_id=cycle.id)
        assert cycles.count() == 1

    def test_list_by_term_type(self, school_year, cycle, term_type_trimester):
        """Test listing by term type."""
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        cycles = SchoolYearCycleSelector.list_by_term_type(
            term_type_id=term_type_trimester.id
        )
        assert cycles.count() == 1

    def test_exists(self, school_year, cycle, term_type_trimester):
        """Test exists method."""
        # Should not exist initially
        assert (
            SchoolYearCycleSelector.exists(
                school_year_id=school_year.id,
                cycle_id=cycle.id,
            )
            is False
        )

        # Create it
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        # Should exist now
        assert (
            SchoolYearCycleSelector.exists(
                school_year_id=school_year.id,
                cycle_id=cycle.id,
            )
            is True
        )

    def test_count_by_school_year(
        self, school_year, cycle, cycle_with_track, term_type_trimester
    ):
        """Test counting cycles by school year."""
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle_with_track,
            term_type=term_type_trimester,
        )

        count = SchoolYearCycleSelector.count_by_school_year(
            school_year_id=school_year.id
        )
        assert count == 2

    def test_search(self, school_year, cycle, term_type_trimester):
        """Test search functionality."""
        SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )

        # Search by cycle name
        results = SchoolYearCycleSelector.search(query="Primaire")
        assert results.count() == 1

        # Search by cycle code
        results = SchoolYearCycleSelector.search(query="PRI")
        assert results.count() == 1

    def test_filter(
        self, school_year, cycle, cycle_with_track, term_type_trimester, term_type_semester
    ):
        """Test filter method."""
        syc1 = SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle,
            term_type=term_type_trimester,
        )
        syc2 = SchoolYearCycle.objects.create(
            school_year=school_year,
            cycle=cycle_with_track,
            term_type=term_type_semester,
        )

        # Filter by cycle
        results = SchoolYearCycleSelector.filter(cycle_id=cycle.id)
        assert results.count() == 1
        assert results.first().id == syc1.id

        # Filter by term type
        results = SchoolYearCycleSelector.filter(term_type_id=term_type_semester.id)
        assert results.count() == 1
        assert results.first().id == syc2.id

        # Filter by school year
        results = SchoolYearCycleSelector.filter(school_year_id=school_year.id)
        assert results.count() == 2
