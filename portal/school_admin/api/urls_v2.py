from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views.teachers import (
    TeacherListView,
    SchoolYearTeacherViewSet,
    SchoolYearTeacherBySchoolYearView,
    TeacherAssignmentViewSet,
    TeacherClassesView,
)

from .views.assessment import (
    AssessmentViewSet,
    AssessmentSubjectViewSet,
    StudentAssessmentViewSet,
    StudentEnrollmentGradesView,
)

from .views.schedule import (
    TimeSlotListView,
    TimeSlotViewSet,
    ClassroomScheduleView,
    TeacherAssignmentScheduleView,
    ScheduleViewSet,
)

from .views.school_year import (
    SchoolYearBySchoolView,
    SchoolYearDetailView,
    SchoolYearCyclesView,
    SchoolYearCycleLevelsView,
    SchoolYearLevelSubjectsView,
    SchoolYearLevelClassroomsView,
    SchoolYearCycleTimeSlotsView,
    SchoolYearConfigureView,
    SchoolYearReconfigureView,
)

app_name = "school_admin_v2"

router = DefaultRouter()
router.register(r"school-year-teachers", SchoolYearTeacherViewSet, basename="school-year-teachers")
router.register(r"teacher-assignments", TeacherAssignmentViewSet, basename="teacher-assignments")
router.register(r"assessments", AssessmentViewSet, basename="assessments")
router.register(r"assessment-subjects", AssessmentSubjectViewSet, basename="assessment-subjects")
router.register(r"student-assessments", StudentAssessmentViewSet, basename="student-assessments")
router.register(r"time-slots", TimeSlotViewSet, basename="time-slots")
router.register(r"schedules", ScheduleViewSet, basename="schedules")

urlpatterns = [
    # Teachers
    path("teachers/", TeacherListView.as_view(), name="teachers-list"),
    path("teachers/<str:teacher_id>/classes/", TeacherClassesView.as_view(), name="teacher-classes"),
    path("school-years/<str:school_year_id>/teachers/", SchoolYearTeacherBySchoolYearView.as_view(), name="school-year-teachers-list"),
    # Assessments - alternate path for student-assessments adapter
    path("assessments/subjects/<str:assessment_subject_id>/grades/", AssessmentSubjectViewSet.as_view({"get": "grades"}), name="assessment-subject-grades-alt"),
    # Student assessments
    path("students/enrollments/<str:enrollment_id>/grades/", StudentEnrollmentGradesView.as_view(), name="student-enrollment-grades"),
    # Schedules
    path("school-year-cycles/<str:school_year_cycle_id>/time-slots/", TimeSlotListView.as_view(), name="school-year-cycle-time-slots"),
    path("classrooms/<str:classroom_id>/schedule/", ClassroomScheduleView.as_view(), name="classroom-schedule"),
    path("teacher-assignments/<str:teacher_assignment_id>/schedule/", TeacherAssignmentScheduleView.as_view(), name="teacher-assignment-schedule"),
    # School Years - V2 read-only (matching frontend ApiSchoolYearAdapter)
    path("schools/<str:school_id>/school-years/", SchoolYearBySchoolView.as_view(), name="schools-school-years"),
    path("schools/school-years/<str:id>/", SchoolYearDetailView.as_view(), name="schools-school-year-detail"),
    path("schools/school-years/<str:school_year_id>/cycles/", SchoolYearCyclesView.as_view(), name="schools-school-year-cycles"),
    path("schools/school-year-cycles/<str:school_year_cycle_id>/levels/", SchoolYearCycleLevelsView.as_view(), name="schools-school-year-cycle-levels"),
    path("schools/school-year-levels/<str:school_year_level_id>/subjects/", SchoolYearLevelSubjectsView.as_view(), name="schools-school-year-level-subjects"),
    path("schools/school-year-levels/<str:school_year_level_id>/classrooms/", SchoolYearLevelClassroomsView.as_view(), name="schools-school-year-level-classrooms"),
    path("schools/school-year-cycles/<str:school_year_cycle_id>/time-slots/", SchoolYearCycleTimeSlotsView.as_view(), name="schools-school-year-cycle-time-slots"),
    # School Years - bulk configuration
    path("schools/configure/", SchoolYearConfigureView.as_view(), name="schools-configure"),
    path("schools/school-years/<str:id>/configure/", SchoolYearReconfigureView.as_view(), name="schools-reconfigure"),
    # Routed endpoints
    path("", include(router.urls)),
]
