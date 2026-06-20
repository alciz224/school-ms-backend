"""
Endpoints helpers pour alimenter les sélecteurs du frontend documents.
Restent minimes et co-localisés ici pour éviter une dépendance circulaire.
"""

from __future__ import annotations

from rest_framework.response import Response
from rest_framework.views import APIView

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.school_operations.models import (
    SchoolYearCycleTerm,
    SchoolYear,
)


class TermsForSchoolYearView(APIView):
    """
    GET /api/v1/documents/terms/?school_year_id=<id>

    Retourne tous les SchoolYearCycleTerm de l'année scolaire (groupés par cycle),
    avec un label prêt à afficher dans un <select>.
    """

    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request):
        sy_id = request.query_params.get("school_year_id")
        if not sy_id:
            return Response({"success": True, "data": []})

        try:
            sy_id_int = int(sy_id)
        except ValueError:
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "invalid_school_year_id",
                        "message": "school_year_id doit être un entier.",
                    },
                },
                status=400,
            )

        if not SchoolYear.objects.filter(id=sy_id_int, is_deleted=False).exists():
            return Response(
                {
                    "success": False,
                    "error": {
                        "code": "school_year_not_found",
                        "message": "Année scolaire introuvable.",
                    },
                },
                status=404,
            )

        qs = (
            SchoolYearCycleTerm.objects.filter(
                school_year_cycle__school_year_id=sy_id_int,
                is_deleted=False,
            )
            .select_related(
                "term",
                "school_year_cycle__cycle",
                "school_year_cycle__term_type",
            )
            .order_by(
                "school_year_cycle__cycle__code",
                "term__order",
            )
        )

        data = [
            {
                "id": str(t.id),
                "term_name": t.term.name or t.term.code,
                "term_code": t.term.code,
                "cycle_name": t.school_year_cycle.cycle.name,
                "cycle_code": t.school_year_cycle.cycle.code,
                "start_date": t.start_date.isoformat() if t.start_date else None,
                "end_date": t.end_date.isoformat() if t.end_date else None,
                # Label complet prêt à afficher
                "label": f"{t.school_year_cycle.cycle.name} — {t.term.name or t.term.code}",
            }
            for t in qs
        ]

        return Response({"success": True, "data": data})
