"""Serializers for Academic domain API."""

from domain.academic.api.serializers.academic_year import AcademicYearSerializer
from domain.academic.api.serializers.assessment_type import AssessmentTypeSerializer
from domain.academic.api.serializers.cycle import CycleSerializer
from domain.academic.api.serializers.level import LevelSerializer
from domain.academic.api.serializers.subject import SubjectSerializer
from domain.academic.api.serializers.term import TermSerializer
from domain.academic.api.serializers.term_type import TermTypeSerializer
from domain.academic.api.serializers.track import TrackSerializer

__all__ = [
    "AcademicYearSerializer",
    "AssessmentTypeSerializer",
    "CycleSerializer",
    "LevelSerializer",
    "SubjectSerializer",
    "TermSerializer",
    "TermTypeSerializer",
    "TrackSerializer",
]
