"""Tests for academic selectors."""
import pytest

from domain.academic.selectors import (
    AcademicYearSelector,
    CycleSelector,
    TrackSelector,
    LevelSelector,
    SubjectSelector,
    AssessmentTypeSelector,
    TermTypeSelector,
    TermSelector,
)
from domain.academic.models import (
    AcademicYear,
    Cycle,
    Track,
    Level,
    Subject,
    AssessmentType,
    TermType,
    Term,
)


@pytest.mark.django_db
class TestAcademicYearSelector:
    """Tests for AcademicYearSelector."""

    def test_list_academic_years(self, academic_year):
        """Test listing all academic years."""
        years = AcademicYearSelector.list()
        assert years.count() == 1
        assert academic_year in years

    def test_get_by_id(self, academic_year):
        """Test getting academic year by ID."""
        result = AcademicYearSelector.get_by_id(year_id=academic_year.id)
        assert result == academic_year

    def test_get_current(self, user):
        """Test getting the current academic year."""
        year = AcademicYear.objects.create(
            start_year=2024,
            end_year=2025,
            is_current=True,
            created_by=user,
            updated_by=user,
        )
        result = AcademicYearSelector.get_current()
        assert result == year


@pytest.mark.django_db
class TestCycleSelector:
    """Tests for CycleSelector."""

    def test_list_cycles(self, cycle):
        """Test listing all cycles."""
        cycles = CycleSelector.list()
        assert cycles.count() == 1
        assert cycle in cycles

    def test_get_by_id(self, cycle):
        """Test getting cycle by ID."""
        result = CycleSelector.get_by_id(cycle_id=cycle.id)
        assert result == cycle

    def test_get_by_code(self, cycle):
        """Test getting cycle by code."""
        result = CycleSelector.get_by_code(code="PRIM")
        assert result == cycle

    def test_get_with_tracks(self, cycle, cycle_with_track):
        """Test getting cycles that have tracks."""
        cycles = CycleSelector.get_with_tracks()
        assert cycles.count() == 1
        assert cycle_with_track in cycles
        assert cycle not in cycles


@pytest.mark.django_db
class TestTrackSelector:
    """Tests for TrackSelector."""

    def test_list_tracks(self, track):
        """Test listing all tracks."""
        tracks = TrackSelector.list()
        assert tracks.count() == 1
        assert track in tracks

    def test_list_by_cycle(self, track, user):
        """Test listing tracks by cycle."""
        # Create another track in same cycle
        Track.objects.create(
            cycle=track.cycle,
            code="SE",
            name="Sciences Économiques",
            created_by=user,
            updated_by=user,
        )
        
        tracks = TrackSelector.list(cycle_id=track.cycle.id)
        assert tracks.count() == 2

    def test_get_by_id(self, track):
        """Test getting track by ID."""
        result = TrackSelector.get_by_id(track_id=track.id)
        assert result == track


@pytest.mark.django_db
class TestLevelSelector:
    """Tests for LevelSelector."""

    def test_list_levels(self, level):
        """Test listing all levels."""
        levels = LevelSelector.list()
        assert levels.count() == 1
        assert level in levels

    def test_list_by_cycle(self, level, user):
        """Test listing levels by cycle."""
        # Create another level in same cycle
        Level.objects.create(
            cycle=level.cycle,
            code="CE1",
            name="Cours Élémentaire 1",
            order=2,
            created_by=user,
            updated_by=user,
        )
        
        levels = LevelSelector.list(cycle_id=level.cycle.id)
        assert levels.count() == 2

    def test_list_by_track(self, cycle_with_track, track, user):
        """Test listing levels by track."""
        # Create levels with track
        Level.objects.create(
            cycle=cycle_with_track,
            track=track,
            code="1S",
            name="Première S",
            order=1,
            created_by=user,
            updated_by=user,
        )
        Level.objects.create(
            cycle=cycle_with_track,
            track=track,
            code="TS",
            name="Terminale S",
            order=2,
            created_by=user,
            updated_by=user,
        )
        
        levels = LevelSelector.list(track_id=track.id)
        assert levels.count() == 2

    def test_get_by_id(self, level):
        """Test getting level by ID."""
        result = LevelSelector.get_by_id(level_id=level.id)
        assert result == level


@pytest.mark.django_db
class TestSubjectSelector:
    """Tests for SubjectSelector."""

    def test_list_subjects(self, subject):
        """Test listing all subjects."""
        subjects = SubjectSelector.list()
        assert subjects.count() == 1
        assert subject in subjects

    def test_get_by_id(self, subject):
        """Test getting subject by ID."""
        result = SubjectSelector.get_by_id(subject_id=subject.id)
        assert result == subject

    def test_get_by_code(self, subject):
        """Test getting subject by code."""
        result = SubjectSelector.get_by_code(code="MATH")
        assert result == subject


@pytest.mark.django_db
class TestAssessmentTypeSelector:
    """Tests for AssessmentTypeSelector."""

    def test_list_assessment_types(self, assessment_type):
        """Test listing all assessment types."""
        types = AssessmentTypeSelector.list()
        assert types.count() == 1
        assert assessment_type in types

    def test_get_by_id(self, assessment_type):
        """Test getting assessment type by ID."""
        result = AssessmentTypeSelector.get_by_id(assessment_type_id=assessment_type.id)
        assert result == assessment_type

    def test_get_by_code(self, assessment_type):
        """Test getting assessment type by code."""
        result = AssessmentTypeSelector.get_by_code(code="EXAM")
        assert result == assessment_type


@pytest.mark.django_db
class TestTermTypeSelector:
    """Tests for TermTypeSelector."""

    def test_list_term_types(self, term_type):
        """Test listing all term types."""
        types = TermTypeSelector.list()
        assert types.count() == 1
        assert term_type in types

    def test_get_by_id(self, term_type):
        """Test getting term type by ID."""
        result = TermTypeSelector.get_by_id(term_type_id=term_type.id)
        assert result == term_type

    def test_get_by_code(self, term_type):
        """Test getting term type by code."""
        result = TermTypeSelector.get_by_code(code="TRIM")
        assert result == term_type


@pytest.mark.django_db
class TestTermSelector:
    """Tests for TermSelector."""

    def test_list_terms(self, term):
        """Test listing all terms."""
        terms = TermSelector.list()
        assert terms.count() == 1
        assert term in terms

    def test_list_by_term_type(self, term, user):
        """Test listing terms by term type."""
        # Create another term
        Term.objects.create(
            term_type=term.term_type,
            order=2,
            code="T2",
            name="Deuxième Trimestre",
            created_by=user,
            updated_by=user,
        )
        
        terms = TermSelector.list(term_type_id=term.term_type.id)
        assert terms.count() == 2

    def test_get_by_id(self, term):
        """Test getting term by ID."""
        result = TermSelector.get_by_id(term_id=term.id)
        assert result == term

    def test_get_by_order(self, term):
        """Test getting term by order."""
        result = TermSelector.get_by_order(
            term_type_id=term.term_type.id,
            order=1
        )
        assert result == term
