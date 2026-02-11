from django.urls import path

from domain.assessment.api.views.bulk import (
    AssessmentSubjectGradesCommitView,
    AssessmentSubjectGradesPreviewView,
)
from domain.assessment.api.views.read import (
    AssessmentOverviewView,
    ClassroomAveragesView,
    ClassroomGradingSheetView,
    StudentGradesHistoryView,
)
from domain.assessment.api.views.status import (
    AssessmentStatusView,
    AssessmentSubjectStatusView,
)

app_name = "assessment"

urlpatterns = [
    # Bulk import
    path(
        "assessment-subjects/<int:assessment_subject_id>/grades/preview/",
        AssessmentSubjectGradesPreviewView.as_view(),
        name="assessment-subject-grades-preview",
    ),
    path(
        "assessment-subjects/<int:assessment_subject_id>/grades/commit/",
        AssessmentSubjectGradesCommitView.as_view(),
        name="assessment-subject-grades-commit",
    ),
    # Read endpoints
    path(
        "assessments/<int:assessment_id>/overview/",
        AssessmentOverviewView.as_view(),
        name="assessment-overview",
    ),
    path(
        "assessment-subjects/<int:assessment_subject_id>/grading-sheet/",
        ClassroomGradingSheetView.as_view(),
        name="assessment-subject-grading-sheet",
    ),
    path(
        "students/<int:enrollment_id>/grades/",
        StudentGradesHistoryView.as_view(),
        name="student-grades-history",
    ),
    path(
        "classrooms/<int:classroom_id>/averages/",
        ClassroomAveragesView.as_view(),
        name="classroom-averages",
    ),
    # Status transitions
    path(
        "assessments/<int:assessment_id>/status/<str:action_name>/",
        AssessmentStatusView.as_view(),
        name="assessment-status",
    ),
    path(
        "assessment-subjects/<int:assessment_subject_id>/status/<str:action_name>/",
        AssessmentSubjectStatusView.as_view(),
        name="assessment-subject-status",
    ),
]
