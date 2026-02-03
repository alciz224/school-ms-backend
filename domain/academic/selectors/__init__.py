"""Academic domain selectors."""

from .academic_year import AcademicYearSelector
from .cycle import CycleSelector
from .level import LevelSelector  
from .subject import SubjectSelector
from .term import TermSelector
from .term_type import TermTypeSelector
from .track import TrackSelector
from .assessment_type import AssessmentTypeSelector

__all__ = [
    "AcademicYearSelector",
    "CycleSelector", 
    "LevelSelector",
    "SubjectSelector",
    "TermSelector",
    "TermTypeSelector",
    "TrackSelector",
    "AssessmentTypeSelector",
]