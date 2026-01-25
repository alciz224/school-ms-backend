# apps/accounts/models/verification.py

"""
Modèles pour la gestion des codes de vérification.
"""

import uuid
import secrets
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from datetime import timedelta

from ..constants import VerificationType, VerificationPurpose


def generate_verification_code() -> str:
    """Génère un code de vérification à 6 chiffres."""
    return "".join(secrets.choice("0123456789") for _ in range(6))


def get_code_expiry() -> timezone.datetime:
    """Retourne la date d'expiration par défaut."""
    config = getattr(settings, "ACCOUNTS_CONFIG", {})
    minutes = config.get("VERIFICATION_CODE_EXPIRY_MINUTES", 10)
    return timezone.now() + timedelta(minutes=minutes)


class VerificationCodeManager(models.Manager):
    """Manager pour les codes de vérification."""

    def create_code(
        self, user, verification_type: str, purpose: str
    ) -> "VerificationCode":
        """
        Crée un nouveau code de vérification.

        Invalide les anciens codes du même type/purpose.
        """
        # Invalider les anciens codes
        self.filter(
            user=user, type=verification_type, purpose=purpose, is_used=False
        ).update(is_used=True)

        # Créer le nouveau
        return self.create(user=user, type=verification_type, purpose=purpose)

    def get_valid_code(
        self, user, code: str, verification_type: str, purpose: str
    ) -> "VerificationCode | None":
        """
        Récupère un code valide s'il existe.
        """
        return self.filter(
            user=user,
            code=code,
            type=verification_type,
            purpose=purpose,
            is_used=False,
            expires_at__gt=timezone.now(),
        ).first()

    def cleanup_expired(self) -> int:
        """
        Supprime les codes expirés.
        Retourne le nombre de codes supprimés.
        """
        result = self.filter(
            models.Q(expires_at__lt=timezone.now()) | models.Q(is_used=True)
        ).delete()
        return result[0]


class VerificationCode(models.Model):
    """
    Code de vérification temporaire.

    Utilisé pour:
        - Vérification de compte (email/phone)
        - Réinitialisation de mot de passe
        - Connexion OTP
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_codes",
        verbose_name=_("Utilisateur"),
    )

    code = models.CharField(
        verbose_name=_("Code"),
        max_length=6,
        default=generate_verification_code,
        db_index=True,
    )

    type = models.CharField(
        verbose_name=_("Type"), max_length=10, choices=VerificationType.choices
    )

    purpose = models.CharField(
        verbose_name=_("But"), max_length=20, choices=VerificationPurpose.choices
    )

    expires_at = models.DateTimeField(
        verbose_name=_("Expire le"), default=get_code_expiry
    )

    attempts = models.PositiveSmallIntegerField(verbose_name=_("Tentatives"), default=0)

    is_used = models.BooleanField(verbose_name=_("Utilisé"), default=False)

    created_at = models.DateTimeField(
        verbose_name=_("Date de création"), auto_now_add=True
    )

    objects = VerificationCodeManager()

    class Meta:
        verbose_name = _("Code de vérification")
        verbose_name_plural = _("Codes de vérification")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user", "type", "purpose", "is_used"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.type}/{self.purpose} - {'Utilisé' if self.is_used else 'Actif'}"

    @property
    def is_expired(self) -> bool:
        """Vérifie si le code est expiré."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Vérifie si le code est encore valide."""
        return not self.is_used and not self.is_expired

    @property
    def max_attempts_reached(self) -> bool:
        """Vérifie si le nombre max de tentatives est atteint."""
        config = getattr(settings, "ACCOUNTS_CONFIG", {})
        max_attempts = config.get("VERIFICATION_MAX_ATTEMPTS", 3)
        return self.attempts >= max_attempts

    @property
    def remaining_attempts(self) -> int:
        """Nombre de tentatives restantes."""
        config = getattr(settings, "ACCOUNTS_CONFIG", {})
        max_attempts = config.get("VERIFICATION_MAX_ATTEMPTS", 3)
        return max(0, max_attempts - self.attempts)

    @property
    def seconds_until_expiry(self) -> int:
        """Secondes restantes avant expiration."""
        if self.is_expired:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, int(delta.total_seconds()))

    def verify(self, code: str) -> bool:
        """
        Vérifie le code fourni.

        Args:
            code: Le code à vérifier

        Returns:
            True si correct, False sinon
        """
        if not self.is_valid:
            return False

        if self.max_attempts_reached:
            return False

        self.attempts += 1

        if self.code == code:
            self.is_used = True
            self.save(update_fields=["attempts", "is_used"])
            return True

        self.save(update_fields=["attempts"])
        return False

    def regenerate(self) -> str:
        """
        Régénère un nouveau code.

        Returns:
            Le nouveau code
        """
        self.code = generate_verification_code()
        self.expires_at = get_code_expiry()
        self.attempts = 0
        self.is_used = False
        self.save()
        return self.code
