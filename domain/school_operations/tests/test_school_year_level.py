"""Tests for SchoolYearLevel model, services, and selectors."""
import pytest
from django.core.exceptions import ValidationError

from domain.school_operations.models import SchoolYearLevel
from domain.school_operations.selectors.school_year_level import SchoolYearLevelSelector
from domain.school_operations.services.school_year_level import SchoolYearLevelService


@pytest.mark.django_db
class TestSchoolYearLevelModel:
    """Test SchoolYearLevel model."""

    def test_create_school_year_level_without_track(
        self, school_year_cycle, level_primary_1
    ):
        """Test creating a school year level without track."""
        school_year_level = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        assert school_year_level.id is not None
        assert school_year_level.school_year_cycle == school_year_cycle
        assert school_year_level.level == level_primary_1
        assert school_year_level.track is None
        assert school_year_level.is_deleted is False

    def test_create_school_year_level_with_track(
        self, school_year_cycle_with_track, level_lycee_terminale, track_sm
    ):
        """Test creating a school year level with track."""
        school_year_level = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle_with_track,
            level=level_lycee_terminale,
            track=track_sm,
        )

        assert school_year_level.id is not None
        assert school_year_level.track == track_sm

    def test_school_year_level_str_without_track(
        self, school_year_cycle, level_primary_1
    ):
        """Test __str__ method without track."""
        school_year_level = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        expected = f"{school_year_cycle.school_year} - {level_primary_1}"
        assert str(school_year_level) == expected

    def test_school_year_level_str_with_track(
        self, school_year_cycle_with_track, level_lycee_terminale, track_sm
    ):
        """Test __str__ method with track."""
        school_year_level = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle_with_track,
            level=level_lycee_terminale,
            track=track_sm,
        )

        expected = f"{school_year_cycle_with_track.school_year} - {level_lycee_terminale} - {track_sm}"
        assert str(school_year_level) == expected

    def test_unique_constraint_with_track(
        self, school_year_cycle_with_track, level_lycee_terminale, track_sm
    ):
        """Test unique constraint on (school_year_cycle, level, track) with non-null track."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle_with_track,
            level=level_lycee_terminale,
            track=track_sm,
        )

        # Should raise error when trying to create duplicate with same track
        with pytest.raises((ValidationError, Exception)):
            SchoolYearLevel.objects.create(
                school_year_cycle=school_year_cycle_with_track,
                level=level_lycee_terminale,
                track=track_sm,
            )

    def test_can_delete(self, school_year_cycle, level_primary_1):
        """Test can_delete method."""
        school_year_level = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        # Should be able to delete when no dependencies
        assert school_year_level.can_delete() is True


@pytest.mark.django_db
class TestSchoolYearLevelService:
    """Test SchoolYearLevelService."""

    def test_create_school_year_level(
        self, school_year_cycle, level_primary_1, user
    ):
        """Test creating a school year level via service."""
        school_year_level = SchoolYearLevelService.create(
            school_year_cycle_id=school_year_cycle.id,
            level_id=level_primary_1.id,
            track_id=None,
            created_by=user,
        )

        assert school_year_level.id is not None
        assert school_year_level.school_year_cycle_id == school_year_cycle.id
        assert school_year_level.level_id == level_primary_1.id
        assert school_year_level.track_id is None
        assert school_year_level.created_by == user
        assert school_year_level.updated_by == user

    def test_create_with_track(
        self, school_year_cycle_with_track, level_lycee_terminale, track_sm, user
    ):
        """Test creating a school year level with track."""
        school_year_level = SchoolYearLevelService.create(
            school_year_cycle_id=school_year_cycle_with_track.id,
            level_id=level_lycee_terminale.id,
            track_id=track_sm.id,
            created_by=user,
        )

        assert school_year_level.track_id == track_sm.id

    def test_create_duplicate_raises_error(
        self, school_year_cycle, level_primary_1, user
    ):
        """Test creating duplicate raises error."""
        SchoolYearLevelService.create(
            school_year_cycle_id=school_year_cycle.id,
            level_id=level_primary_1.id,
            track_id=None,
            created_by=user,
        )

        # Should raise error on duplicate
        with pytest.raises((ValidationError, Exception)):
            SchoolYearLevelService.create(
                school_year_cycle_id=school_year_cycle.id,
                level_id=level_primary_1.id,
                track_id=None,
                created_by=user,
            )

    def test_update_school_year_level(
        self, school_year_cycle_with_track, level_lycee_terminale, track_sm, track_se, user
    ):
        """Test updating a school year level."""
        school_year_level = SchoolYearLevelService.create(
            school_year_cycle_id=school_year_cycle_with_track.id,
            level_id=level_lycee_terminale.id,
            track_id=track_sm.id,
            created_by=user,
        )

        # Update track
        updated = SchoolYearLevelService.update(
            school_year_level=school_year_level,
            track_id=track_se.id,
            updated_by=user,
        )

        assert updated.track_id == track_se.id
        assert updated.updated_by == user

    def test_delete_school_year_level(
        self, school_year_cycle, level_primary_1, user
    ):
        """Test soft deleting a school year level."""
        school_year_level = SchoolYearLevelService.create(
            school_year_cycle_id=school_year_cycle.id,
            level_id=level_primary_1.id,
            track_id=None,
            created_by=user,
        )

        deleted = SchoolYearLevelService.delete(
            school_year_level=school_year_level,
            deleted_by=user,
        )

        assert deleted.is_deleted is True
        assert deleted.is_active is False
        assert deleted.deleted_by == user
        assert deleted.deleted_at is not None

    def test_restore_school_year_level(
        self, school_year_cycle, level_primary_1, user
    ):
        """Test restoring a soft-deleted school year level."""
        school_year_level = SchoolYearLevelService.create(
            school_year_cycle_id=school_year_cycle.id,
            level_id=level_primary_1.id,
            track_id=None,
            created_by=user,
        )

        # Delete it
        SchoolYearLevelService.delete(
            school_year_level=school_year_level,
            deleted_by=user,
        )

        # Restore it
        restored = SchoolYearLevelService.restore(
            school_year_level=school_year_level,
            updated_by=user,
        )

        assert restored.is_deleted is False
        assert restored.deleted_by is None
        assert restored.deleted_at is None

    def test_bulk_create_for_cycle(
        self, school_year_cycle, level_primary_1, level_primary_2, user
    ):
        """Test bulk creating level configurations."""
        level_configs = [
            {"level_id": level_primary_1.id, "track_id": None},
            {"level_id": level_primary_2.id, "track_id": None},
        ]

        created_levels = SchoolYearLevelService.bulk_create_for_cycle(
            school_year_cycle_id=school_year_cycle.id,
            level_configs=level_configs,
            created_by=user,
        )

        assert len(created_levels) == 2
        assert created_levels[0].level_id == level_primary_1.id
        assert created_levels[1].level_id == level_primary_2.id


@pytest.mark.django_db
class TestSchoolYearLevelSelector:
    """Test SchoolYearLevelSelector."""

    def test_get_by_id(self, school_year_cycle, level_primary_1):
        """Test getting by ID."""
        school_year_level = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        found = SchoolYearLevelSelector.get_by_id(id=school_year_level.id)
        assert found is not None
        assert found.id == school_year_level.id

    def test_get_by_unique_fields(self, school_year_cycle, level_primary_1):
        """Test getting by unique fields."""
        school_year_level = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        found = SchoolYearLevelSelector.get_by_unique_fields(
            school_year_cycle_id=school_year_cycle.id,
            level_id=level_primary_1.id,
            track_id=None,
        )

        assert found is not None
        assert found.id == school_year_level.id

    def test_list_by_school_year_cycle(
        self, school_year_cycle, level_primary_1, level_primary_2
    ):
        """Test listing levels by school year cycle."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_2,
            track=None,
        )

        levels = SchoolYearLevelSelector.list_by_school_year_cycle(
            school_year_cycle_id=school_year_cycle.id
        )

        assert levels.count() == 2

    def test_list_by_school_year(
        self, school_year_cycle, level_primary_1
    ):
        """Test listing levels by school year."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        levels = SchoolYearLevelSelector.list_by_school_year(
            school_year_id=school_year_cycle.school_year_id
        )

        assert levels.count() == 1

    def test_list_by_school(self, school_year_cycle, level_primary_1):
        """Test listing levels by school."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        levels = SchoolYearLevelSelector.list_by_school(
            school_id=school_year_cycle.school_year.school_id
        )

        assert levels.count() == 1

    def test_list_by_level(self, school_year_cycle, level_primary_1):
        """Test listing by level."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        levels = SchoolYearLevelSelector.list_by_level(level_id=level_primary_1.id)
        assert levels.count() == 1

    def test_list_by_track(
        self, school_year_cycle_with_track, level_lycee_terminale, track_sm
    ):
        """Test listing by track."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle_with_track,
            level=level_lycee_terminale,
            track=track_sm,
        )

        levels = SchoolYearLevelSelector.list_by_track(track_id=track_sm.id)
        assert levels.count() == 1

    def test_exists(self, school_year_cycle, level_primary_1):
        """Test exists method."""
        # Should not exist initially
        assert (
            SchoolYearLevelSelector.exists(
                school_year_cycle_id=school_year_cycle.id,
                level_id=level_primary_1.id,
                track_id=None,
            )
            is False
        )

        # Create it
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        # Should exist now
        assert (
            SchoolYearLevelSelector.exists(
                school_year_cycle_id=school_year_cycle.id,
                level_id=level_primary_1.id,
                track_id=None,
            )
            is True
        )

    def test_count_by_school_year_cycle(
        self, school_year_cycle, level_primary_1, level_primary_2
    ):
        """Test counting levels by school year cycle."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_2,
            track=None,
        )

        count = SchoolYearLevelSelector.count_by_school_year_cycle(
            school_year_cycle_id=school_year_cycle.id
        )
        assert count == 2

    def test_search(self, school_year_cycle, level_primary_1):
        """Test search functionality."""
        SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )

        # Search by level name
        results = SchoolYearLevelSelector.search(query="1ère")
        assert results.count() == 1

        # Search by level code
        results = SchoolYearLevelSelector.search(query="1A")
        assert results.count() == 1

    def test_filter(
        self, school_year_cycle, level_primary_1, level_primary_2
    ):
        """Test filter method."""
        syl1 = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_1,
            track=None,
        )
        syl2 = SchoolYearLevel.objects.create(
            school_year_cycle=school_year_cycle,
            level=level_primary_2,
            track=None,
        )

        # Filter by level
        results = SchoolYearLevelSelector.filter(level_id=level_primary_1.id)
        assert results.count() == 1
        assert results.first().id == syl1.id

        # Filter by school year cycle
        results = SchoolYearLevelSelector.filter(
            school_year_cycle_id=school_year_cycle.id
        )
        assert results.count() == 2
