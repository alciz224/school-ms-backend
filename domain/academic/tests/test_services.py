"""Tests for academic services."""
import pytest
from django.core.exceptions import ValidationError

from domain.academic.services import (
    AcademicYearService,
    CycleService,
    TrackService,
    LevelService,
    SubjectService,
    AssessmentTypeService,
    TermTypeService,
    TermService,
)


@pytest.mark.django_db
class TestAcademicYearService:
    """Tests for AcademicYearService."""

    def test_create_academic_year(self, user):
        """Test creating an academic year."""
        year = AcademicYearService.create(
            start_year=2024,
            end_year=2025,
            user=user,
        )
        assert year.code == "2024-2025"
        assert year.created_by == user

    def test_update_academic_year(self, academic_year, user):
        """Test updating an academic year."""
        updated = AcademicYearService.update(
            academic_year=academic_year,
            status="COMPLETED",
            user=user,
        )
        assert updated.status == "COMPLETED"
        assert updated.updated_by == user

    def test_delete_academic_year(self, academic_year, user):
        """Test soft deleting an academic year."""
        AcademicYearService.delete(academic_year=academic_year, user=user)
        assert academic_year.is_deleted is True


@pytest.mark.django_db
class TestCycleService:
    """Tests for CycleService."""

    def test_create_cycle(self, user):
        """Test creating a cycle."""
        cycle = CycleService.create(
            code="prim",  # Test case conversion
            name="  Primaire  ",  # Test trimming
            has_track=False,
            user=user,
        )
        assert cycle.code == "PRIM"
        assert cycle.name == "Primaire"
        assert cycle.has_track is False

    def test_update_cycle(self, cycle, user):
        """Test updating a cycle."""
        updated = CycleService.update(
            cycle=cycle,
            name="École Primaire",
            user=user,
        )
        assert updated.name == "École Primaire"

    def test_delete_cycle(self, cycle, user):
        """Test soft deleting a cycle."""
        CycleService.delete(cycle=cycle, user=user)
        assert cycle.is_deleted is True


@pytest.mark.django_db
class TestTrackService:
    """Tests for TrackService."""

    def test_create_track(self, cycle_with_track, user):
        """Test creating a track."""
        track = TrackService.create(
            cycle=cycle_with_track,
            code="st",
            name="Sciences et Technologies",
            user=user,
        )
        assert track.code == "ST"
        assert track.cycle == cycle_with_track

    def test_update_track(self, track, user):
        """Test updating a track."""
        updated = TrackService.update(
            track=track,
            name="Sciences et Techniques",
            user=user,
        )
        assert updated.name == "Sciences et Techniques"

    def test_delete_track(self, track, user):
        """Test soft deleting a track."""
        TrackService.delete(track=track, user=user)
        assert track.is_deleted is True


@pytest.mark.django_db
class TestLevelService:
    """Tests for LevelService."""

    def test_create_level(self, cycle, user):
        """Test creating a level."""
        level = LevelService.create(
            cycle=cycle,
            code="cp",
            name="Cours Préparatoire",
            order=1,
            user=user,
        )
        assert level.code == "CP"
        assert level.cycle == cycle

    def test_create_level_with_track(self, cycle_with_track, track, user):
        """Test creating a level with a track."""
        level = LevelService.create(
            cycle=cycle_with_track,
            track=track,
            code="TS",
            name="Terminale Sciences",
            order=3,
            user=user,
        )
        assert level.track == track

    def test_update_level(self, level, user):
        """Test updating a level."""
        updated = LevelService.update(
            level=level,
            name="CP - Cours Préparatoire",
            user=user,
        )
        assert updated.name == "CP - Cours Préparatoire"

    def test_delete_level(self, level, user):
        """Test soft deleting a level."""
        LevelService.delete(level=level, user=user)
        assert level.is_deleted is True


@pytest.mark.django_db
class TestSubjectService:
    """Tests for SubjectService."""

    def test_create_subject(self, user):
        """Test creating a subject."""
        subject = SubjectService.create(
            code="math",
            name="  Mathématiques  ",
            user=user,
        )
        assert subject.code == "MATH"
        assert subject.name == "Mathématiques"

    def test_update_subject(self, subject, user):
        """Test updating a subject."""
        updated = SubjectService.update(
            subject=subject,
            name="Mathématiques Générales",
            user=user,
        )
        assert updated.name == "Mathématiques Générales"

    def test_delete_subject(self, subject, user):
        """Test soft deleting a subject."""
        SubjectService.delete(subject=subject, user=user)
        assert subject.is_deleted is True


@pytest.mark.django_db
class TestAssessmentTypeService:
    """Tests for AssessmentTypeService."""

    def test_create_assessment_type(self, user):
        """Test creating an assessment type."""
        assessment_type = AssessmentTypeService.create(
            code="exam",
            name="Examen",
            user=user,
        )
        assert assessment_type.code == "EXAM"
        assert assessment_type.name == "Examen"

    def test_update_assessment_type(self, assessment_type, user):
        """Test updating an assessment type."""
        updated = AssessmentTypeService.update(
            assessment_type=assessment_type,
            name="Examen Final",
            user=user,
        )
        assert updated.name == "Examen Final"

    def test_delete_assessment_type(self, assessment_type, user):
        """Test soft deleting an assessment type."""
        AssessmentTypeService.delete(assessment_type=assessment_type, user=user)
        assert assessment_type.is_deleted is True


@pytest.mark.django_db
class TestTermTypeService:
    """Tests for TermTypeService."""

    def test_create_term_type(self, user):
        """Test creating a term type."""
        term_type = TermTypeService.create(
            code="trim",
            name="Trimestre",
            number_of_terms=3,
            user=user,
        )
        assert term_type.code == "TRIM"
        assert term_type.number_of_terms == 3

    def test_update_term_type(self, term_type, user):
        """Test updating a term type."""
        updated = TermTypeService.update(
            term_type=term_type,
            name="Système Trimestriel",
            user=user,
        )
        assert updated.name == "Système Trimestriel"

    def test_delete_term_type(self, term_type, user):
        """Test soft deleting a term type."""
        TermTypeService.delete(term_type=term_type, user=user)
        assert term_type.is_deleted is True


@pytest.mark.django_db
class TestTermService:
    """Tests for TermService."""

    def test_create_term(self, term_type, user):
        """Test creating a term."""
        term = TermService.create(
            term_type=term_type,
            order=1,
            code="t1",
            name="Premier Trimestre",
            user=user,
        )
        assert term.code == "T1"
        assert term.order == 1
        assert term.term_type == term_type

    def test_update_term(self, term, user):
        """Test updating a term."""
        updated = TermService.update(
            term=term,
            name="1er Trimestre",
            user=user,
        )
        assert updated.name == "1er Trimestre"

    def test_delete_term(self, term, user):
        """Test soft deleting a term."""
        TermService.delete(term=term, user=user)
        assert term.is_deleted is True
