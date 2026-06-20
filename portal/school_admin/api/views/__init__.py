from .students import SchoolAdminStudentListView, SchoolAdminStudentDetailView
from .parents import SchoolAdminParentListView, SchoolAdminParentDetailView
from .teachers import TeacherListView, SchoolYearTeacherViewSet, SchoolYearTeacherBySchoolYearView, TeacherAssignmentViewSet, TeacherClassesView

from .assessment import (
    AssessmentViewSet,
    AssessmentSubjectViewSet,
    StudentAssessmentViewSet,
    StudentEnrollmentGradesView,
)

from .schedule import (
    TimeSlotListView,
    TimeSlotViewSet,
    ClassroomScheduleView,
    TeacherAssignmentScheduleView,
    ScheduleViewSet,
)

from .reports import (
    ReportCardListView,
    ReportCardDetailView,
    TranscriptListView,
    TranscriptDetailView,
)

__all__ = [
    "SchoolAdminStudentListView", 
    "SchoolAdminStudentDetailView",
    "SchoolAdminParentListView",
    "SchoolAdminParentDetailView",
    "TeacherListView",
    "SchoolYearTeacherViewSet",
    "SchoolYearTeacherBySchoolYearView",
    "TeacherAssignmentViewSet",
    "TeacherClassesView",
    "AssessmentViewSet",
    "AssessmentSubjectViewSet",
    "StudentAssessmentViewSet",
    "StudentEnrollmentGradesView",
    "TimeSlotListView",
    "TimeSlotViewSet",
    "ClassroomScheduleView",
    "TeacherAssignmentScheduleView",
    "ScheduleViewSet",
    "ReportCardListView",
    "ReportCardDetailView",
    "TranscriptListView",
    "TranscriptDetailView",
]
