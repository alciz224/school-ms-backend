"""
School operations API views.
"""

from .school import SchoolViewSet
from .school_year import SchoolYearViewSet
from .school_year_cycle import SchoolYearCycleViewSet
from .school_year_cycle_time_slot import SchoolYearCycleTimeSlotViewSet
from .school_year_level import SchoolYearLevelViewSet
from .school_year_teacher import SchoolYearTeacherViewSet

__all__ = [
    'SchoolViewSet',
    'SchoolYearViewSet',
    'SchoolYearCycleViewSet',
    'SchoolYearCycleTimeSlotViewSet',
    'SchoolYearLevelViewSet',
    'SchoolYearTeacherViewSet',
]
