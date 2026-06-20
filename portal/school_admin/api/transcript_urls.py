from django.urls import path, re_path

from portal.school_admin.api.views.reports import TranscriptListView, TranscriptDetailView

app_name = "school_admin_transcripts"

urlpatterns = [
    path("", TranscriptListView.as_view(), name="transcripts-list"),
    re_path(r"^(?P<pk>[^/.]+)/$", TranscriptDetailView.as_view(), name="transcripts-detail"),
]
