"""
URL patterns for school operations API.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.school_operations.api.views import SchoolYearViewSet
from domain.school_operations.api.views.school_year_cycle import SchoolYearCycleViewSet
from domain.school_operations.api.views.school_year_level import SchoolYearLevelViewSet

app_name = "school_operations"

# Configure router
router = DefaultRouter()
router.register(r'school-years', SchoolYearViewSet, basename='school-year')
router.register(r'school-year-cycles', SchoolYearCycleViewSet, basename='school-year-cycle')
router.register(r'school-year-levels', SchoolYearLevelViewSet, basename='school-year-level')

urlpatterns = [
    path("", include(router.urls)),
]