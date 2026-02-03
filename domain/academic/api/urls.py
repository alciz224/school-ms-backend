"""URL configuration for Academic domain API."""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from domain.academic.api.views import (
    AcademicYearViewSet,
    AssessmentTypeViewSet,
    CycleViewSet,
    LevelViewSet,
    SubjectViewSet,
    TermViewSet,
    TermTypeViewSet,
    TrackViewSet,
)

app_name = "academic"

router = DefaultRouter()
router.register(r"academic-years", AcademicYearViewSet, basename="academic-year")
router.register(r"cycles", CycleViewSet, basename="cycle")
router.register(r"tracks", TrackViewSet, basename="track")
router.register(r"levels", LevelViewSet, basename="level")
router.register(r"subjects", SubjectViewSet, basename="subject")
router.register(r"assessment-types", AssessmentTypeViewSet, basename="assessment-type")
router.register(r"term-types", TermTypeViewSet, basename="term-type")
router.register(r"terms", TermViewSet, basename="term")

urlpatterns = [
    path("", include(router.urls)),
]
