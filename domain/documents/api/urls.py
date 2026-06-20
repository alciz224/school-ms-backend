"""URLs du domaine documents."""

from django.urls import path

from domain.documents.api.views.bulk_views import (
    BulkDocumentPreviewView,
    BulkDocumentPrintView,
)
from domain.documents.api.views.document_views import (
    DocumentPreviewView,
    DocumentPrintView,
)
from domain.documents.api.views.helpers_views import TermsForSchoolYearView


app_name = "documents"

urlpatterns = [
    # Document unique
    path(
        "preview/<str:document_type>/<int:enrollment_id>/",
        DocumentPreviewView.as_view(),
        name="preview",
    ),
    path(
        "print/<str:document_type>/<int:enrollment_id>/",
        DocumentPrintView.as_view(),
        name="print",
    ),

    # Bulk : aperçu et impression d'une classe entière (HTML multi-pages)
    path(
        "bulk-preview/<str:document_type>/",
        BulkDocumentPreviewView.as_view(),
        name="bulk-preview",
    ),
    path(
        "bulk-print/<str:document_type>/",
        BulkDocumentPrintView.as_view(),
        name="bulk-print",
    ),

    # Helpers
    path(
        "terms/",
        TermsForSchoolYearView.as_view(),
        name="terms-for-school-year",
    ),
]
