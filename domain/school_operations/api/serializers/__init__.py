"""
School operations API serializers.
"""

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
from .school_year_level import (
    SchoolYearLevelSerializer,
    SchoolYearLevelListSerializer,
    SchoolYearLevelCreateSerializer,
    SchoolYearLevelUpdateSerializer,
    SchoolYearLevelBulkCreateSerializer,
)

__all__ = [
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
    'SchoolYearLevelSerializer',
    'SchoolYearLevelListSerializer',
    'SchoolYearLevelCreateSerializer',
    'SchoolYearLevelUpdateSerializer',
    'SchoolYearLevelBulkCreateSerializer',
]
