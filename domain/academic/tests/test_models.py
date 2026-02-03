"""Tests for Academic domain models."""
import pytest
from django.core.exceptions import ValidationError

from domain.academic.models import (
    AcademicYear,
    AssessmentType,
    Cycle,
    Level,
    Subject,
    Term,
    TermType,
    Track,
)


@pytest.mark.django_db
class TestAcademicYear:
    """Tests for AcademicYear model."""

    def test_create_academic_year(self):
        """Test creating an academic year."""
        year = AcademicYear.objects.create(
            start_year=2024,
            end_year=2025,
            status="ACTIVE",
        )
        assert year.code == "2024-2025"
        assert str(year) == "2024-2025"

    def test_only_one_current_year(self):
        """Test that only one year can be current."""
        year1 = AcademicYear.objects.create(
            start_year=2024,
            end_year=2025,
            is_current=True,
        )
        assert year1.is_current

        # Creating another current year will fail validation
        with pytest.raises(ValidationError):
            year2 = AcademicYear(
                start_year=2025,
                end_year=2026,
                is_current=True,
            )
            year2.full_clean()
        
        # But if we create it, it auto-updates the previous one
        year2 = AcademicYear.objects.create(
            start_year=2025,
            end_year=2026,
            is_current=False,
        )
        year2.is_current = True
        year2.save()
        
        year1.refresh_from_db()
        assert not year1.is_current
        assert year2.is_current

    def test_invalid_year_sequence(self):
        """Test validation of year sequence."""
        with pytest.raises(ValidationError):
            year = AcademicYear(
                start_year=2024,
                end_year=2026,  # Invalid: should be 2025
            )
            year.full_clean()

    def test_get_current(self):
        """Test getting current academic year."""
        AcademicYear.objects.create(
            start_year=2024,
            end_year=2025,
            is_current=True,
        )
        current = AcademicYear.objects.get_current()
        assert current is not None
        assert current.code == "2024-2025"

    def test_archive_year(self):
        """Test archiving an academic year."""
        year = AcademicYear.objects.create(
            start_year=2024,
            end_year=2025,
            is_current=True,
            status="ACTIVE",
        )
        year.archive()
        assert year.status == "ARCHIVED"
        assert not year.is_current


@pytest.mark.django_db
class TestCycle:
    """Tests for Cycle model."""

    def test_create_cycle(self):
        """Test creating a cycle."""
        cycle = Cycle.objects.create(
            code="PRI",
            name="Primaire",
            has_track=False,
        )
        assert str(cycle) == "Primaire (PRI)"

    def test_cycle_with_tracks(self):
        """Test creating a cycle that supports tracks."""
        cycle = Cycle.objects.create(
            code="LYC",
            name="Lycée",
            has_track=True,
        )
        assert cycle.has_track


@pytest.mark.django_db
class TestTrack:
    """Tests for Track model."""

    def test_create_track(self):
        """Test creating a track."""
        cycle = Cycle.objects.create(
            code="LYC",
            name="Lycée",
            has_track=True,
        )
        track = Track.objects.create(
            code="SM",
            name="Sciences Mathématiques",
            cycle=cycle,
        )
        assert str(track) == "Sciences Mathématiques (SM)"

    def test_track_requires_cycle_with_has_track(self):
        """Test that track can only be created for cycles with has_track=True."""
        cycle = Cycle.objects.create(
            code="PRI",
            name="Primaire",
            has_track=False,
        )
        with pytest.raises(ValidationError):
            track = Track(
                code="TEST",
                name="Test Track",
                cycle=cycle,
            )
            track.full_clean()


@pytest.mark.django_db
class TestLevel:
    """Tests for Level model."""

    def test_create_level_without_track(self):
        """Test creating a level without track."""
        cycle = Cycle.objects.create(
            code="PRI",
            name="Primaire",
            has_track=False,
        )
        level = Level.objects.create(
            code="CE1",
            name="Cours Élémentaire 1",
            cycle=cycle,
            order=1,
        )
        assert str(level) == "Cours Élémentaire 1"

    def test_create_level_with_track(self):
        """Test creating a level with track."""
        cycle = Cycle.objects.create(
            code="LYC",
            name="Lycée",
            has_track=True,
        )
        track = Track.objects.create(
            code="SM",
            name="Sciences Mathématiques",
            cycle=cycle,
        )
        level = Level.objects.create(
            code="TER_SM",
            name="Terminale SM",
            cycle=cycle,
            track=track,
            order=3,
        )
        assert "SM" in str(level)

    def test_level_track_required_validation(self):
        """Test that track is required for cycles with has_track=True."""
        cycle = Cycle.objects.create(
            code="LYC",
            name="Lycée",
            has_track=True,
        )
        with pytest.raises(ValidationError):
            level = Level(
                code="TER",
                name="Terminale",
                cycle=cycle,
                order=3,
            )
            level.full_clean()


@pytest.mark.django_db
class TestSubject:
    """Tests for Subject model."""

    def test_create_subject(self):
        """Test creating a subject."""
        subject = Subject.objects.create(
            code="MATH",
            name="Mathématiques",
            description="Mathematics subject",
        )
        assert str(subject) == "Mathématiques (MATH)"


@pytest.mark.django_db
class TestAssessmentType:
    """Tests for AssessmentType model."""

    def test_create_assessment_type(self):
        """Test creating an assessment type."""
        assessment_type = AssessmentType.objects.create(
            code="COMPO",
            name="Composition",
            description="Formal examination",
        )
        assert str(assessment_type) == "Composition (COMPO)"


@pytest.mark.django_db
class TestTermType:
    """Tests for TermType model."""

    def test_create_term_type(self):
        """Test creating a term type."""
        term_type = TermType.objects.create(
            code="TRIMESTER",
            name="Trimestre",
            period_count=3,
        )
        assert "3 periods" in str(term_type)

    def test_invalid_period_count(self):
        """Test validation of period count."""
        with pytest.raises(ValidationError):
            term_type = TermType(
                code="INVALID",
                name="Invalid",
                period_count=0,
            )
            term_type.full_clean()


@pytest.mark.django_db
class TestTerm:
    """Tests for Term model."""

    def test_create_term(self):
        """Test creating a term."""
        term_type = TermType.objects.create(
            code="TRIMESTER",
            name="Trimestre",
            period_count=3,
        )
        term = Term.objects.create(
            term_type=term_type,
            code="T1",
            name="Trimestre 1",
            order=1,
        )
        assert str(term) == "T1 - Trimestre 1"

    def test_term_order_validation(self):
        """Test validation of term order."""
        term_type = TermType.objects.create(
            code="TRIMESTER",
            name="Trimestre",
            period_count=3,
        )
        with pytest.raises(ValidationError):
            term = Term(
                term_type=term_type,
                code="T4",
                name="Trimestre 4",
                order=4,  # Invalid: exceeds period_count
            )
            term.full_clean()
