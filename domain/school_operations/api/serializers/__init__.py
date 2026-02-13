"""
School operations API serializers.
"""

from .school import SchoolSerializer
from .school_year import (
    SchoolYearListSerializer,
    SchoolYearDetailSerializer,
    SchoolYearCreateSerializer,
    SchoolYearUpdateSerializer,
    SchoolYearStatusSerializer,
    SchoolYearHolidaySerializer,
    SchoolYearSettingSerializer,
    SchoolYearStatisticsSerializer,
)
from .school_year_cycle import (
    SchoolYearCycleSerializer,
    SchoolYearCycleListSerializer,
    SchoolYearCycleCreateSerializer,
    SchoolYearCycleUpdateSerializer,
    SchoolYearCycleBulkCreateSerializer,
)
from .school_year_cycle_time_slot import SchoolYearCycleTimeSlotSerializer
from .school_year_level import (
    SchoolYearLevelSerializer,
    SchoolYearLevelListSerializer,
    SchoolYearLevelCreateSerializer,
    SchoolYearLevelUpdateSerializer,
    SchoolYearLevelBulkCreateSerializer,
)
from .school_year_teacher import SchoolYearTeacherSerializer

__all__ = [
    'SchoolSerializer',
    'SchoolYearListSerializer',
    'SchoolYearDetailSerializer',
    'SchoolYearCreateSerializer',
    'SchoolYearUpdateSerializer',
    'SchoolYearStatusSerializer',
    'SchoolYearHolidaySerializer',
    'SchoolYearSettingSerializer',
    'SchoolYearStatisticsSerializer',
    'SchoolYearCycleSerializer',
    'SchoolYearCycleListSerializer',
    'SchoolYearCycleCreateSerializer',
    'SchoolYearCycleUpdateSerializer',
    'SchoolYearCycleBulkCreateSerializer',
    'SchoolYearCycleTimeSlotSerializer',
    'SchoolYearLevelSerializer',
    'SchoolYearLevelListSerializer',
    'SchoolYearLevelCreateSerializer',
    'SchoolYearLevelUpdateSerializer',
    'SchoolYearLevelBulkCreateSerializer',
    'SchoolYearTeacherSerializer',
]
