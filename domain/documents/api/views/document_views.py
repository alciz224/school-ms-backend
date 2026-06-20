"""
Vues API pour les documents académiques.

Deux endpoints par document :
    GET  /api/v1/documents/preview/<type>/<enrollment_id>/  -> HTML pour iframe
    GET  /api/v1/documents/print/<type>/<enrollment_id>/    -> HTML + auto-print

L'enregistrement en PDF est délégué au navigateur via le dialogue
d'impression natif ("Enregistrer au format PDF").
"""

from __future__ import annotations

import logging

from django.http import HttpResponse
from rest_framework.views import APIView

from domain.documents.services.context_builders import CONTEXT_BUILDERS
from domain.documents.services.html_renderer import (
    TEMPLATE_MAP,
    render_document_html,
)
from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.enrollment.models import StudentEnrollment
from domain.school_operations.models import SchoolYearCycleTerm


logger = logging.getLogger(__name__)


ALLOWED_TYPES = set(TEMPLATE_MAP.keys())


def _load_enrollment(enrollment_id: int) -> StudentEnrollment | None:
    """Charge un StudentEnrollment avec tous les FK utiles préchargés."""
    return (
        StudentEnrollment.objects.select_related(
            "student__user",
            "student__place_of_birth",
            "classroom",
            "school_year_level__level",
            "school_year_level__track",
            "school_year_level__school_year_cycle__cycle",
            "school_year_level__school_year_cycle__term_type",
            "school_year_level__school_year_cycle__school_year__school__locality__administrative_unit",
            "school_year_level__school_year_cycle__school_year__academic_year",
            "school_year_level__school_year_cycle__school_year__school__director",
        )
        .filter(id=enrollment_id, is_deleted=False)
        .first()
    )


def _load_term(term_id: int | None) -> SchoolYearCycleTerm | None:
    if not term_id:
        return None
    return (
        SchoolYearCycleTerm.objects.select_related("term", "school_year_cycle")
        .filter(id=term_id, is_deleted=False)
        .first()
    )


def _build_context_or_error(
    document_type: str,
    enrollment_id: int,
    term_id: int | None,
) -> tuple[dict | None, HttpResponse | None]:
    """Charge l'enrollment + term et construit le contexte. Retourne (ctx, error_response)."""
    if document_type not in ALLOWED_TYPES:
        return None, HttpResponse(
            f"<h1>Type de document inconnu : {document_type}</h1>",
            status=400,
            content_type="text/html; charset=utf-8",
        )

    enrollment = _load_enrollment(enrollment_id)
    if enrollment is None:
        return None, HttpResponse(
            "<h1>Inscription élève introuvable.</h1>",
            status=404,
            content_type="text/html; charset=utf-8",
        )

    term = _load_term(term_id)

    builder_class = CONTEXT_BUILDERS.get(document_type)
    if builder_class is None:
        return None, HttpResponse(
            f"<h1>Pas de builder pour {document_type}.</h1>",
            status=400,
            content_type="text/html; charset=utf-8",
        )

    try:
        context = builder_class(enrollment=enrollment, term=term).build()
    except ValueError as exc:
        return None, HttpResponse(
            f"<h1>{exc}</h1>", status=400, content_type="text/html; charset=utf-8",
        )

    return context, None


# =============================================================================
# Vues
# =============================================================================

class DocumentPreviewView(APIView):
    """HTML pour iframe — c'est le MÊME HTML qui sert au PDF."""
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, document_type: str, enrollment_id: int):
        term_id = request.query_params.get("term_id")
        try:
            term_id_int = int(term_id) if term_id else None
        except ValueError:
            return HttpResponse(
                "<h1>term_id doit être un entier.</h1>",
                status=400,
                content_type="text/html; charset=utf-8",
            )

        context, error = _build_context_or_error(document_type, enrollment_id, term_id_int)
        if error:
            return error

        html = render_document_html(
            document_type=document_type,
            context=context,
            preview_mode=True,
        )
        return HttpResponse(html, content_type="text/html; charset=utf-8")


class DocumentPrintView(APIView):
    """HTML + script auto-print pour impression directe depuis le navigateur."""
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, document_type: str, enrollment_id: int):
        term_id = request.query_params.get("term_id")
        try:
            term_id_int = int(term_id) if term_id else None
        except ValueError:
            return HttpResponse(
                "<h1>term_id invalide.</h1>",
                status=400,
                content_type="text/html; charset=utf-8",
            )

        context, error = _build_context_or_error(document_type, enrollment_id, term_id_int)
        if error:
            return error

        html = render_document_html(
            document_type=document_type,
            context=context,
            preview_mode=False,
        )

        # Injecter le script d'auto-print juste avant </body>
        print_script = (
            "<script>window.addEventListener('load', function() {"
            "setTimeout(function() { window.print(); }, 500); });</script>"
        )
        html = html.replace("</body>", f"{print_script}</body>")

        return HttpResponse(html, content_type="text/html; charset=utf-8")
