"""School operations domain selectors."""

from .school import SchoolSelector
from .school_year_cycle import SchoolYearCycleSelector
from .school_year_cycle_term import SchoolYearCycleTermSelector
from .school_year_cycle_time_slot import SchoolYearCycleTimeSlotSelector
from .school_year_level import SchoolYearLevelSelector
from .school_year_level_subject import SchoolYearLevelSubjectSelector
from .school_year_teacher import SchoolYearTeacherSelector

__all__ = [
    "SchoolSelector",
    "SchoolYearCycleSelector",
    "SchoolYearCycleTermSelector",
    "SchoolYearCycleTimeSlotSelector",
    "SchoolYearLevelSelector",
    "SchoolYearLevelSubjectSelector",
    "SchoolYearTeacherSelector",
]
