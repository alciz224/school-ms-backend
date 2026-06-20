from django.urls import path, re_path

from portal.school_admin.api.views.reports import ReportCardListView, ReportCardDetailView

app_name = "school_admin_reports"

urlpatterns = [
    path("", ReportCardListView.as_view(), name="report-cards-list"),
    re_path(r"^(?P<pk>[^/.]+)/$", ReportCardDetailView.as_view(), name="report-cards-detail"),
]
