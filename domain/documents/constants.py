"""Constantes du domaine documents."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class DocumentType(models.TextChoices):
    """Types de documents générables."""

    BULLETIN = "bulletin", _("Bulletin de notes")
    TRANSCRIPT = "transcript", _("Relevé de notes annuel")
    ATTESTATION = "attestation", _("Attestation de scolarité")
    CERTIFICAT = "certificat", _("Certificat de scolarité")
    CARTE = "carte", _("Carte scolaire")


class DocumentStatus(models.TextChoices):
    """Statut d'une demande de génération."""

    PENDING = "pending", _("En attente")
    GENERATING = "generating", _("En cours")
    COMPLETED = "completed", _("Terminé")
    FAILED = "failed", _("Échoué")
