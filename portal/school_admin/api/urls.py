from django.urls import path

from .views.students import SchoolAdminStudentListView, SchoolAdminStudentDetailView
from .views.parents import SchoolAdminParentListView, SchoolAdminParentDetailView
from .views.finance import (
    FeeTypeListView,
    SchoolFeeCreateView,
    SchoolFeeUpdateView,
    StudentPaymentCreateView,
    FeeSummaryListView,
)

app_name = "school_admin"

urlpatterns = [
    path("students/", SchoolAdminStudentListView.as_view(), name="students-list"),
    path("students/<str:pk>/", SchoolAdminStudentDetailView.as_view(), name="students-detail"),

    path("parents/", SchoolAdminParentListView.as_view(), name="parents-list"),
    path("parents/<str:pk>/", SchoolAdminParentDetailView.as_view(), name="parents-detail"),

    # Finance
    path("fee-types/", FeeTypeListView.as_view(), name="fee-types-list"),
    path("fees/summaries/", FeeSummaryListView.as_view(), name="fees-summaries"),
    path("fees/", SchoolFeeCreateView.as_view(), name="fees-create"),
    path("fees/<str:pk>/", SchoolFeeUpdateView.as_view(), name="fees-update"),
    path("payments/", StudentPaymentCreateView.as_view(), name="payments-create"),
]
