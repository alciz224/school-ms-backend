"""Academic domain services."""

from .academic_year import AcademicYearService
from .cycle import CycleService  
from .level import LevelService
from .subject import SubjectService
from .term import TermService
from .term_type import TermTypeService
from .track import TrackService
from .assessment_type import AssessmentTypeService

__all__ = [
    "AcademicYearService",
    "CycleService",
    "LevelService", 
    "SubjectService",
    "TermService",
    "TermTypeService",
    "TrackService",
    "AssessmentTypeService",
]