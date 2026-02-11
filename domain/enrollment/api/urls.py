from django.urls import include, path
from rest_framework.routers import DefaultRouter

from domain.enrollment.api.views.classroom import ClassroomViewSet
from domain.enrollment.api.views.roster import (
    ClassroomRosterViewSet,
    MyChildrenEnrollmentsView,
    MyClassesView,
    MyEnrollmentsView,
    SchoolYearLevelEnrollmentsView,
)
from domain.enrollment.api.views.student_enrollment import StudentEnrollmentViewSet
from domain.enrollment.api.views.teacher_assignment import TeacherAssignmentViewSet

app_name = "enrollment"

router = DefaultRouter()
router.register(r"classrooms", ClassroomViewSet, basename="enrollment-classroom")
router.register(r"student-enrollments", StudentEnrollmentViewSet, basename="enrollment-student-enrollment")
router.register(r"teacher-assignments", TeacherAssignmentViewSet, basename="enrollment-teacher-assignment")

# Portal-oriented roster endpoints
router.register(r"roster/classrooms", ClassroomRosterViewSet, basename="enrollment-roster-classroom")

urlpatterns = [
    path("", include(router.urls)),
    # School year level enrollments (for school admin/staff)
    path(
        "roster/school-year-levels/<int:school_year_level_id>/enrollments/",
        SchoolYearLevelEnrollmentsView.as_view(),
        name="roster-school-year-level-enrollments",
    ),
    # Student portal: my enrollments
    path("roster/me/", MyEnrollmentsView.as_view(), name="roster-my-enrollments"),
    # Parent portal: my children's enrollments
    path("roster/my-children/", MyChildrenEnrollmentsView.as_view(), name="roster-my-children-enrollments"),
    # Teacher portal: my assigned classes
    path("roster/my-classes/", MyClassesView.as_view(), name="roster-my-classes"),
]
