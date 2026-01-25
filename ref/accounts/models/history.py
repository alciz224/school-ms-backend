# apps/accounts/models/history.py

"""
Modèles pour l'historique et le suivi.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from ..constants import PhoneRemovalReason, LoginFailureReason


class PhoneHistory(models.Model):
    """
    Historique des numéros de téléphone d'un utilisateur.

    Utile pour:
        - Traçabilité des changements
        - Récupération si nouveau numéro perdu
        - Sécurité (détecter les patterns suspects)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phone_history",
        verbose_name=_("Utilisateur"),
    )

    phone = models.CharField(verbose_name=_("Numéro de téléphone"), max_length=20)

    verified = models.BooleanField(
        verbose_name=_("Était vérifié"),
        default=False,
        help_text=_("Le numéro était-il vérifié avant retrait ?"),
    )

    added_at = models.DateTimeField(
        verbose_name=_("Date d'ajout"),
        help_text=_("Quand le numéro a été ajouté au compte."),
    )

    removed_at = models.DateTimeField(
        verbose_name=_("Date de retrait"), default=timezone.now
    )

    reason = models.CharField(
        verbose_name=_("Raison"),
        max_length=20,
        choices=PhoneRemovalReason.choices,
        default=PhoneRemovalReason.CHANGED,
    )

    class Meta:
        verbose_name = _("Historique téléphone")
        verbose_name_plural = _("Historiques téléphones")
        ordering = ["-removed_at"]

        indexes = [
            models.Index(fields=["user", "removed_at"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.phone} ({self.reason})"

    def save(self, *args, **kwargs):
        # Si added_at n'est pas défini, utiliser la date d'inscription
        if not self.added_at:
            self.added_at = self.user.date_joined
        super().save(*args, **kwargs)


class LoginAttempt(models.Model):
    """
    Enregistre les tentatives de connexion.

    Utile pour:
        - Rate limiting
        - Détection de brute-force
        - Audit de sécurité
        - Alerter l'utilisateur d'activité suspecte
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    identifier = models.CharField(
        verbose_name=_("Identifiant utilisé"),
        max_length=255,
        help_text=_("Email ou téléphone utilisé pour la tentative."),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="login_attempts",
        verbose_name=_("Utilisateur"),
        help_text=_("NULL si le compte n'existe pas."),
    )

    ip_address = models.GenericIPAddressField(verbose_name=_("Adresse IP"))

    user_agent = models.TextField(verbose_name=_("User Agent"), blank=True, default="")

    success = models.BooleanField(verbose_name=_("Réussie"), default=False)

    failure_reason = models.CharField(
        verbose_name=_("Raison de l'échec"),
        max_length=30,
        choices=LoginFailureReason.choices,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date"), auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = _("Tentative de connexion")
        verbose_name_plural = _("Tentatives de connexion")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["identifier", "created_at"]),
            models.Index(fields=["ip_address", "created_at"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["success", "created_at"]),
        ]

    def __str__(self):
        status = "✓" if self.success else "✗"
        return f"{status} {self.identifier} - {self.ip_address}"

    @classmethod
    def record(
        cls,
        identifier: str,
        ip_address: str,
        user=None,
        success: bool = False,
        failure_reason: str = None,
        user_agent: str = "",
    ) -> "LoginAttempt":
        """
        Enregistre une tentative de connexion.
        """
        return cls.objects.create(
            identifier=identifier,
            user=user,
            ip_address=ip_address,
            success=success,
            failure_reason=failure_reason,
            user_agent=user_agent,
        )

    @classmethod
    def get_recent_failures(
        cls, identifier: str = None, ip_address: str = None, minutes: int = 30
    ) -> int:
        """
        Compte les échecs récents pour un identifiant ou IP.
        """
        since = timezone.now() - timezone.timedelta(minutes=minutes)

        queryset = cls.objects.filter(success=False, created_at__gte=since)

        if identifier:
            queryset = queryset.filter(identifier=identifier)

        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)

        return queryset.count()

    @classmethod
    def is_locked_out(cls, identifier: str = None, ip_address: str = None) -> bool:
        """
        Vérifie si l'identifiant ou l'IP est bloqué.
        """
        config = getattr(settings, "ACCOUNTS_CONFIG", {})
        max_attempts = config.get("LOGIN_MAX_ATTEMPTS", 5)
        lockout_minutes = config.get("LOGIN_LOCKOUT_MINUTES", 30)

        failures = cls.get_recent_failures(
            identifier=identifier, ip_address=ip_address, minutes=lockout_minutes
        )

        return failures >= max_attempts
