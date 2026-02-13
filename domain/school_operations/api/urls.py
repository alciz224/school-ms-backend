"""
URL patterns for school operations API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.school_operations.api.views import (
    SchoolViewSet,
    SchoolYearViewSet,
    SchoolYearCycleViewSet,
    SchoolYearCycleTimeSlotViewSet,
    SchoolYearLevelViewSet,
    SchoolYearTeacherViewSet,
)
from domain.school_operations.api.views.school_year_cycle_term import SchoolYearCycleTermViewSet
from domain.school_operations.api.views.school_year_level_subject import SchoolYearLevelSubjectViewSet

app_name = "school_operations"

# Configure router
router = DefaultRouter()
router.register(r'schools', SchoolViewSet, basename='school')
router.register(r'school-years', SchoolYearViewSet, basename='school-year')
router.register(r'school-year-cycles', SchoolYearCycleViewSet, basename='school-year-cycle')
router.register(r'school-year-cycle-terms', SchoolYearCycleTermViewSet, basename='school-year-cycle-term')
router.register(r'school-year-cycle-time-slots', SchoolYearCycleTimeSlotViewSet, basename='school-year-cycle-time-slot')
router.register(r'school-year-levels', SchoolYearLevelViewSet, basename='school-year-level')
router.register(r'school-year-level-subjects', SchoolYearLevelSubjectViewSet, basename='school-year-level-subject')
router.register(r'school-year-teachers', SchoolYearTeacherViewSet, basename='school-year-teacher')

urlpatterns = [
    path("", include(router.urls)),
]