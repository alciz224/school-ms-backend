"""
Aperçu et impression en masse.

Stratégie : assemble en une seule page HTML tous les documents d'une classe.
Chaque document est un `<div class="document-page">` séparé par un saut de
page CSS. L'utilisateur peut imprimer ou enregistrer en PDF via le dialogue
natif du navigateur (Ctrl+P → "Enregistrer au format PDF").
"""

from __future__ import annotations

import logging
import re

from django.http import HttpResponse
from django.template.loader import render_to_string
from rest_framework.views import APIView

from domain.documents.services.context_builders import CONTEXT_BUILDERS
from domain.documents.services.html_renderer import (
    TEMPLATE_MAP,
    render_document_html,
)
from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.enrollment.models import Classroom


logger = logging.getLogger(__name__)


# Regex pour extraire le contenu du <body> d'un HTML rendu.
_BODY_RE = re.compile(r"<body[^>]*>(.*)</body>", re.DOTALL | re.IGNORECASE)


def _select_classroom_enrollments(classroom_id: int):
    """Charge la classe + les inscriptions actives avec tous les FK utiles."""
    try:
        classroom = Classroom.objects.select_related(
            "school_year_level__school_year_cycle__school_year__school"
        ).get(id=classroom_id, is_deleted=False)
    except Classroom.DoesNotExist:
        return None, None

    enrollments = list(
        classroom.student_enrollments.filter(is_deleted=False)
        .select_related(
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
        .order_by("last_name", "first_name")
    )
    return classroom, enrollments


def _render_bulk_html(
    *,
    document_type: str,
    classroom: Classroom,
    enrollments: list,
    term,
    preview_mode: bool,
) -> str:
    """Assemble un HTML unique contenant tous les documents."""
    builder_class = CONTEXT_BUILDERS[document_type]

    pages: list[str] = []
    for enrollment in enrollments:
        try:
            ctx = builder_class(enrollment=enrollment, term=term).build()
            full_html = render_document_html(
                document_type=document_type,
                context=ctx,
                preview_mode=False,
            )
            m = _BODY_RE.search(full_html)
            if m:
                pages.append(m.group(1).strip())
        except Exception as exc:
            logger.warning(
                "Bulk render failed for %s: %s", enrollment, exc,
            )
            pages.append(
                f'<div class="document-page" style="display:flex;align-items:center;justify-content:center;color:#c53030;">'
                f"Erreur pour {enrollment} : {exc}"
                f"</div>"
            )

    return render_to_string(
        "documents/bulk_wrapper.html",
        {
            "title": f"{classroom.name} — {document_type}",
            "count": len(pages),
            "pages_html": "\n".join(pages),
            "preview_mode": preview_mode,
            "base_url": __import__("django.conf", fromlist=["settings"]).settings.DOCUMENT_BASE_URL,
        },
    )


def _resolve_term(request) -> tuple[object, HttpResponse | None]:
    """Résout le term_id query param. Retourne (term_or_None, error_response)."""
    term_id = request.query_params.get("term_id")
    if not term_id:
        return None, None
    try:
        term_id_int = int(term_id)
    except ValueError:
        return None, HttpResponse(
            "<h1>term_id invalide.</h1>",
            status=400,
            content_type="text/html; charset=utf-8",
        )
    from domain.school_operations.models import SchoolYearCycleTerm
    term = SchoolYearCycleTerm.objects.filter(
        id=term_id_int, is_deleted=False
    ).first()
    return term, None


def _validate_request(request, document_type: str):
    """Validations communes aux deux vues bulk. Retourne (classroom, enrollments, term, error_response)."""
    if document_type not in TEMPLATE_MAP:
        return None, None, None, HttpResponse(
            f"<h1>Type de document inconnu : {document_type}</h1>",
            status=400,
            content_type="text/html; charset=utf-8",
        )

    classroom_id = request.query_params.get("classroom_id")
    if not classroom_id:
        return None, None, None, HttpResponse(
            "<h1>classroom_id est obligatoire.</h1>",
            status=400,
            content_type="text/html; charset=utf-8",
        )
    try:
        classroom_id_int = int(classroom_id)
    except ValueError:
        return None, None, None, HttpResponse(
            "<h1>classroom_id invalide.</h1>",
            status=400,
            content_type="text/html; charset=utf-8",
        )

    classroom, enrollments = _select_classroom_enrollments(classroom_id_int)
    if classroom is None:
        return None, None, None, HttpResponse(
            "<h1>Classe introuvable.</h1>",
            status=404,
            content_type="text/html; charset=utf-8",
        )
    if not enrollments:
        return None, None, None, HttpResponse(
            "<h1>Aucun élève actif dans cette classe.</h1>",
            status=200,
            content_type="text/html; charset=utf-8",
        )

    term, term_err = _resolve_term(request)
    if term_err:
        return None, None, None, term_err

    return classroom, enrollments, term, None


# =============================================================================
# Vues
# =============================================================================

class BulkDocumentPreviewView(APIView):
    """
    GET /api/v1/documents/bulk-preview/<type>/?classroom_id=X&term_id=Y

    Retourne un seul HTML contenant tous les documents d'une classe,
    affichables dans une iframe ou une nouvelle fenêtre. Inclut une barre
    d'action "Imprimer / Enregistrer en PDF" qui appelle window.print().
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, document_type: str):
        classroom, enrollments, term, error = _validate_request(request, document_type)
        if error:
            return error

        html = _render_bulk_html(
            document_type=document_type,
            classroom=classroom,
            enrollments=enrollments,
            term=term,
            preview_mode=True,
        )
        return HttpResponse(html, content_type="text/html; charset=utf-8")


class BulkDocumentPrintView(APIView):
    """
    GET /api/v1/documents/bulk-print/<type>/?classroom_id=X&term_id=Y

    Variante avec auto-print au chargement. Idéale ouverte dans un popup.
    L'utilisateur peut soit imprimer, soit choisir "Enregistrer au format PDF"
    dans le dialogue du navigateur.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, document_type: str):
        classroom, enrollments, term, error = _validate_request(request, document_type)
        if error:
            return error

        html = _render_bulk_html(
            document_type=document_type,
            classroom=classroom,
            enrollments=enrollments,
            term=term,
            preview_mode=False,
        )
        # Injecte un auto-print
        script = (
            "<script>window.addEventListener('load', function() {"
            "setTimeout(function() { window.print(); }, 700); });</script>"
        )
        html = html.replace("</body>", f"{script}</body>")
        return HttpResponse(html, content_type="text/html; charset=utf-8")
