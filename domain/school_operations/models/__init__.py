"""
School operations models.
"""

from .school import School
from .school_year import SchoolYear
from .school_year_cycle import SchoolYearCycle
from .school_year_cycle_term import SchoolYearCycleTerm
from .school_year_cycle_time_slot import SchoolYearCycleTimeSlot
from .school_year_level import SchoolYearLevel
from .school_year_level_subject import SchoolYearLevelSubject
from .school_year_teacher import SchoolYearTeacher

__all__ = [
    "School",
    "SchoolYear",
    "SchoolYearCycle",
    "SchoolYearCycleTerm",
    "SchoolYearCycleTimeSlot",
    "SchoolYearLevel",
    "SchoolYearLevelSubject",
    "SchoolYearTeacher",
]