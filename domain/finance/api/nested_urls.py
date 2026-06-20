"""
URL patterns for frontend-adapter paths that live under /api/v1/ directly.

The frontend finance adapter expects paths like:
  /api/v1/school-years/{id}/fees/
  /api/v1/student-enrollments/{id}/payments/
  /api/v1/classrooms/{id}/payments/

These are included from config/urls.py at the /api/v1/ prefix.
"""
from django.urls import path

from domain.finance.api.views.school_fee import SchoolFeeViewSet
from domain.finance.api.views.student_payment import StudentPaymentViewSet
from domain.finance.api.views.finance_portal import (
    EnrollmentPaymentsListView,
    ClassroomPaymentsListView,
    FinanceStatsView,
)

app_name = "finance_nested"

urlpatterns = [
    # /api/v1/school-years/{schoolYearId}/fees/
    path(
        "school-years/<int:school_year_id>/fees/",
        SchoolFeeViewSet.as_view({"get": "list"}),
        name="school-year-fees",
    ),
    # /api/v1/school-years/{schoolYearId}/fees/stats/
    path(
        "school-years/<int:school_year_id>/fees/stats/",
        FinanceStatsView.as_view(),
        name="school-year-fees-stats",
    ),
    # /api/v1/student-enrollments/{studentEnrollmentId}/payments/
    path(
        "student-enrollments/<int:student_enrollment_id>/payments/",
        EnrollmentPaymentsListView.as_view(),
        name="student-enrollment-payments",
    ),
    # /api/v1/classrooms/{classroomId}/payments/
    path(
        "classrooms/<int:classroom_id>/payments/",
        ClassroomPaymentsListView.as_view(),
        name="classroom-payments",
    ),
]
