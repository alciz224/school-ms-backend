"""Views for Academic domain API."""

from domain.academic.api.views.academic_year import AcademicYearViewSet
from domain.academic.api.views.assessment_type import AssessmentTypeViewSet
from domain.academic.api.views.cycle import CycleViewSet
from domain.academic.api.views.level import LevelViewSet
from domain.academic.api.views.subject import SubjectViewSet
from domain.academic.api.views.term import TermViewSet
from domain.academic.api.views.term_type import TermTypeViewSet
from domain.academic.api.views.track import TrackViewSet

__all__ = [
    "AcademicYearViewSet",
    "AssessmentTypeViewSet",
    "CycleViewSet",
    "LevelViewSet",
    "SubjectViewSet",
    "TermViewSet",
    "TermTypeViewSet",
    "TrackViewSet",
]
