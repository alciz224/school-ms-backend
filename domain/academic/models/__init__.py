"""Academic domain models."""

from domain.academic.models.academic_year import AcademicYear
from domain.academic.models.assessment_type import AssessmentType
from domain.academic.models.cycle import Cycle
from domain.academic.models.level import Level
from domain.academic.models.subject import Subject
from domain.academic.models.term import Term
from domain.academic.models.term_type import TermType
from domain.academic.models.track import Track

__all__ = [
    "AcademicYear",
    "AssessmentType",
    "Cycle",
    "Level",
    "Subject",
    "Term",
    "TermType",
    "Track",
]
