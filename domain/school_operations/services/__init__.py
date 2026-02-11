"""School operations domain services."""

from .school import SchoolService
from .school_year_cycle import SchoolYearCycleService
from .school_year_cycle_term import SchoolYearCycleTermService
from .school_year_cycle_time_slot import SchoolYearCycleTimeSlotService
from .school_year_level import SchoolYearLevelService
from .school_year_level_subject import SchoolYearLevelSubjectService
from .school_year_teacher import SchoolYearTeacherService

__all__ = [
    "SchoolService",
    "SchoolYearCycleService",
    "SchoolYearCycleTermService",
    "SchoolYearCycleTimeSlotService",
    "SchoolYearLevelService",
    "SchoolYearLevelSubjectService",
    "SchoolYearTeacherService",
]
