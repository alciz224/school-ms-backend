"""Modèles du domaine documents — traçabilité des générations."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.documents.constants import DocumentStatus, DocumentType
from domain.shared.models.base import AuditModel


class DocumentRequest(AuditModel):
    """
    Trace chaque génération de document (preview, PDF, impression).

    Permet :
        - Audit complet : qui a généré quoi, quand
        - Cache de fichiers identiques via file_hash
        - Statistiques de génération
        - Récupération du dernier PDF généré sans tout regénérer
    """

    document_type = models.CharField(
        max_length=20,
        choices=DocumentType.choices,
        db_index=True,
        verbose_name=_("Type de document"),
    )

    # Cible : un élève + une période optionnelle
    student_enrollment = models.ForeignKey(
        "enrollment.StudentEnrollment",
        on_delete=models.PROTECT,
        related_name="document_requests",
        verbose_name=_("Inscription élève"),
        help_text=_("Inscription pour laquelle le document est généré."),
    )
    school_year_cycle_term = models.ForeignKey(
        "school_operations.SchoolYearCycleTerm",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="document_requests",
        verbose_name=_("Période"),
        help_text=_("Période concernée (obligatoire pour bulletin/relevé)."),
    )

    status = models.CharField(
        max_length=20,
        choices=DocumentStatus.choices,
        default=DocumentStatus.PENDING,
        db_index=True,
        verbose_name=_("Statut"),
    )

    generated_file = models.FileField(
        upload_to="generated_documents/",
        null=True,
        blank=True,
        verbose_name=_("Fichier généré"),
    )
    generated_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Généré le"),
    )

    file_hash = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_("Empreinte SHA-256"),
        help_text=_("Permet de détecter les générations identiques."),
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Taille du fichier (octets)"),
    )

    error_message = models.TextField(
        blank=True,
        verbose_name=_("Message d'erreur"),
    )

    class Meta:
        db_table = "document_request"
        verbose_name = _("Demande de document")
        verbose_name_plural = _("Demandes de documents")
        ordering = ["-created_at"]
        indexes = [
            models.Index(
                fields=["student_enrollment", "document_type", "school_year_cycle_term"],
                name="doc_req_lookup_idx",
            ),
            models.Index(fields=["status"], name="doc_req_status_idx"),
            models.Index(fields=["file_hash"], name="doc_req_hash_idx"),
        ]

    def __str__(self) -> str:
        return (
            f"{self.get_document_type_display()} — "
            f"{self.student_enrollment} ({self.get_status_display()})"
        )
