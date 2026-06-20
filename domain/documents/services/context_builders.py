"""
Construction des contextes Django pour chaque type de document.

Chaque builder est responsable de fournir un dict prêt à être passé au template,
à partir des modèles métier (StudentEnrollment, ReportCard, SchoolYear, etc.).

Séparation stricte données / rendu : aucun HTML ici.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from django.conf import settings

from domain.enrollment.models import StudentEnrollment
from domain.school_operations.models import SchoolYearCycleTerm


# -----------------------------------------------------------------------------
# Helpers communs
# -----------------------------------------------------------------------------

def _rank_suffix_fr(rank: int) -> str:
    """Suffixe ordinal français : 1er, 2ème, 3ème..."""
    return "er" if rank == 1 else "ème"


def _grade_css_class(average: Decimal | float | None) -> str:
    """Classe CSS selon la moyenne (excellent / good / average / poor)."""
    if average is None:
        return ""
    avg = float(average)
    if avg >= 16:
        return "grade-excellent"
    if avg >= 14:
        return "grade-good"
    if avg >= 10:
        return "grade-average"
    return "grade-poor"


def _full_name_from_enrollment(enrollment: StudentEnrollment) -> str:
    """Nom complet d'un élève (depuis profil utilisateur si dispo, sinon snapshot)."""
    if enrollment.student_id and enrollment.student.user_id:
        u = enrollment.student.user
        return f"{u.first_name} {u.last_name}".strip()
    return f"{enrollment.first_name} {enrollment.last_name}".strip()


def _gender_suffix_fr(enrollment: StudentEnrollment) -> str:
    """Renvoie 'e' si féminin pour les accords ('inscrite', 'née'), '' sinon."""
    if not enrollment.student_id:
        return ""
    profile = enrollment.student
    return "e" if getattr(profile, "gender", None) == "F" else ""


# -----------------------------------------------------------------------------
# Builders
# -----------------------------------------------------------------------------

class BaseContextBuilder:
    """Contexte de base partagé par tous les documents."""

    def __init__(
        self,
        enrollment: StudentEnrollment,
        term: SchoolYearCycleTerm | None = None,
    ):
        self.enrollment = enrollment
        self.term = term

        # Résolution école / année / niveau via les FK existantes
        syl = enrollment.school_year_level
        syc = syl.school_year_cycle if syl else None
        sy = syc.school_year if syc else None

        self.school_year_level = syl
        self.school_year_cycle = syc
        self.school_year = sy
        self.school = sy.school if sy else None

    def base_context(self) -> dict[str, Any]:
        base_url = getattr(settings, "DOCUMENT_BASE_URL", "http://localhost:8000")
        student_full_name = _full_name_from_enrollment(self.enrollment)

        return {
            "base_url": base_url,
            "generation_date": datetime.now(),

            # École & année
            "school": self.school,
            "academic_year_code": (
                self.school_year.academic_year.code if self.school_year else ""
            ),

            # Élève
            "enrollment": self.enrollment,
            "student_full_name": student_full_name,
            "annual_identifier": self.enrollment.annual_identifier,
            "classroom_name": (
                self.enrollment.classroom.name if self.enrollment.classroom else "—"
            ),

            # Niveau / cycle
            "level_name": (
                self.school_year_level.level.name if self.school_year_level else ""
            ),
            "track_name": (
                self.school_year_level.track.name
                if self.school_year_level and self.school_year_level.track
                else ""
            ),
            "cycle_name": (
                self.school_year_cycle.cycle.name if self.school_year_cycle else ""
            ),

            # Signataires (override possible par les sous-classes)
            "signers": self._default_signers(),
        }

    def _default_signers(self) -> list[dict[str, Any]]:
        """3 signataires standards : professeur principal, parent, directeur."""
        location = (
            self.school.locality.administrative_unit.name
            if self.school and self.school.locality
            else ""
        )
        director = self.school.director if self.school else None
        director_name = (
            f"{director.first_name} {director.last_name}".strip() if director else ""
        )
        return [
            {
                "title": "Le Professeur Principal",
                "name": "",
                "signature_image": None,
                "location": location,
            },
            {
                "title": "Le Parent / Tuteur",
                "name": "",
                "signature_image": None,
                "location": location,
            },
            {
                "title": "Le Directeur",
                "name": director_name,
                "signature_image": None,
                "location": location,
            },
        ]

    def build(self) -> dict[str, Any]:
        """À surcharger par chaque type de document."""
        return self.base_context()


class BulletinContextBuilder(BaseContextBuilder):
    """Bulletin de notes pour une période (trimestre / semestre)."""

    def build(self) -> dict[str, Any]:
        from domain.assessment.models import ReportCard, ReportCardSubject

        ctx = self.base_context()

        if self.term is None:
            raise ValueError("Le bulletin nécessite une période (term).")

        # On récupère le bulletin existant ou on construit à la volée
        report_card = (
            ReportCard.objects.filter(
                student_enrollment=self.enrollment,
                school_year_cycle_term=self.term,
                is_deleted=False,
            )
            .select_related("classroom")
            .first()
        )

        # Lignes de matières
        subject_rows: list[dict[str, Any]] = []
        total_weighted = Decimal("0")
        total_coefficients = Decimal("0")

        if report_card is not None:
            subjects_qs = (
                ReportCardSubject.objects.filter(
                    report_card=report_card,
                    is_deleted=False,
                )
                .select_related("school_year_level_subject__subject")
                .order_by("school_year_level_subject__subject__name")
            )
            for s in subjects_qs:
                avg = s.average
                coef = s.coefficient
                weighted = (avg * coef) if avg is not None and coef is not None else None
                subject_rows.append({
                    "subject_name": s.school_year_level_subject.subject.name,
                    "coefficient": coef,
                    "average": avg,
                    "weighted": weighted,
                    "css_class": _grade_css_class(avg),
                })
                if weighted is not None:
                    total_weighted += weighted
                if coef is not None:
                    total_coefficients += coef

        # Effectif de la classe
        class_size = 0
        if self.enrollment.classroom_id:
            class_size = self.enrollment.classroom.student_enrollments.filter(
                is_deleted=False
            ).count()

        ctx.update({
            "term_label": self.term.term.name or self.term.term.code,
            "term_type_name": self.school_year_cycle.term_type.name if self.school_year_cycle else "",
            "subject_rows": subject_rows,
            "overall_average": report_card.overall_average if report_card else None,
            "student_rank": report_card.rank if report_card else None,
            "rank_suffix": _rank_suffix_fr(report_card.rank) if report_card and report_card.rank else "",
            "total_weighted": total_weighted if total_weighted else None,
            "total_coefficients": total_coefficients,
            "class_size": class_size,
            "decision": report_card.decision if report_card else "",
        })
        return ctx


class AttestationContextBuilder(BaseContextBuilder):
    """Attestation de scolarité — un seul signataire (le directeur)."""

    def build(self) -> dict[str, Any]:
        ctx = self.base_context()
        ctx["signers"] = [ctx["signers"][-1]]  # Garde uniquement le directeur

        # Champs additionnels propres à l'attestation
        director = self.school.director if self.school else None
        ctx["director_name"] = (
            f"{director.first_name} {director.last_name}".strip() if director else ""
        )
        ctx["director_title"] = "Directeur"

        profile = self.enrollment.student if self.enrollment.student_id else None
        ctx["date_of_birth"] = profile.date_of_birth if profile else None
        ctx["place_of_birth"] = (
            profile.place_of_birth.name if profile and profile.place_of_birth else ""
        )
        ctx["gender_suffix"] = _gender_suffix_fr(self.enrollment)

        return ctx


class CertificatContextBuilder(AttestationContextBuilder):
    """Certificat de scolarité — variante de l'attestation avec numéro de certificat."""

    def build(self) -> dict[str, Any]:
        ctx = super().build()
        now = datetime.now()
        school_code = self.school.code if self.school else "ECO"
        ctx["certificate_number"] = (
            f"CERT-{school_code}-{now.strftime('%Y%m%d')}-{self.enrollment.annual_identifier}"
        )
        return ctx


class TranscriptContextBuilder(BaseContextBuilder):
    """Relevé annuel — agrégation des ReportCard de l'année scolaire."""

    @staticmethod
    def _mention_for(avg: Decimal | None) -> str:
        if avg is None:
            return ""
        a = float(avg)
        if a >= 16:
            return "Très Bien"
        if a >= 14:
            return "Bien"
        if a >= 12:
            return "Assez Bien"
        if a >= 10:
            return "Passable"
        return "Insuffisant"

    def build(self) -> dict[str, Any]:
        from domain.assessment.models import ReportCard, Transcript

        ctx = self.base_context()

        report_cards = (
            ReportCard.objects.filter(
                student_enrollment=self.enrollment,
                school_year_cycle_term__school_year_cycle__school_year=self.school_year,
                is_deleted=False,
            )
            .select_related("school_year_cycle_term__term", "classroom")
            .order_by("school_year_cycle_term__term__order")
        )

        class_size = 0
        if self.enrollment.classroom_id:
            class_size = self.enrollment.classroom.student_enrollments.filter(
                is_deleted=False
            ).count()

        term_rows: list[dict[str, Any]] = []
        sum_avg = Decimal("0")
        count_avg = 0
        for rc in report_cards:
            avg = rc.overall_average
            term_rows.append({
                "term_label": rc.school_year_cycle_term.term.name or rc.school_year_cycle_term.term.code,
                "average": avg,
                "rank": rc.rank,
                "class_size": class_size,
                "decision": rc.decision,
                "css_class": _grade_css_class(avg),
            })
            if avg is not None:
                sum_avg += avg
                count_avg += 1

        annual_average = (
            (sum_avg / count_avg).quantize(Decimal("0.01")) if count_avg else None
        )

        transcript = (
            Transcript.objects.filter(
                student_enrollment=self.enrollment,
                school_year=self.school_year,
                is_deleted=False,
            )
            .first()
        )
        if transcript and transcript.overall_average is not None:
            annual_average = transcript.overall_average

        ctx.update({
            "term_rows": term_rows,
            "annual_average": annual_average,
            "mention": self._mention_for(annual_average),
            "decision": transcript.decision if transcript else "",
        })
        return ctx


class CarteContextBuilder(BaseContextBuilder):
    """Carte scolaire — pièce d'identité élève pour l'année scolaire."""

    def build(self) -> dict[str, Any]:
        ctx = self.base_context()
        # Une seule signature : le directeur
        ctx["signers"] = [ctx["signers"][-1]]

        profile = self.enrollment.student if self.enrollment.student_id else None
        ctx["date_of_birth"] = profile.date_of_birth if profile else None
        ctx["place_of_birth"] = (
            profile.place_of_birth.name if profile and profile.place_of_birth else ""
        )

        gender = getattr(profile, "gender", None) if profile else None
        ctx["gender_display"] = (
            "Féminin" if gender == "F" else ("Masculin" if gender == "M" else "—")
        )

        base_url = getattr(settings, "DOCUMENT_BASE_URL", "http://localhost:8000")
        if profile and profile.photo:
            ctx["photo_url"] = f"{base_url}{profile.photo.url}"
        else:
            ctx["photo_url"] = ""

        ctx["valid_from"] = self.school_year.start_date if self.school_year else None
        ctx["valid_to"] = self.school_year.end_date if self.school_year else None
        return ctx


# Registre des builders par type de document
CONTEXT_BUILDERS: dict[str, type[BaseContextBuilder]] = {
    "bulletin": BulletinContextBuilder,
    "attestation": AttestationContextBuilder,
    "certificat": CertificatContextBuilder,
    "transcript": TranscriptContextBuilder,
    "carte": CarteContextBuilder,
}
