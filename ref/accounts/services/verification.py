# domain/accounts/services/verification.py

"""
Service de vérification.
Gère: envoi de codes, confirmation, statut.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from domain.accounts.models import CustomUser, VerificationCode
from domain.accounts.constants import VerificationType, VerificationPurpose
from domain.accounts.exceptions import (
    NoContactToVerifyError,
    AlreadyVerifiedError,
    VerificationCooldownError,
    VerificationCodeInvalidError,
    VerificationCodeExpiredError,
    VerificationMaxAttemptsError,
)

from .notifications import get_notification_service

logger = logging.getLogger(__name__)


@dataclass
class SendCodeResult:
    """Résultat de l'envoi d'un code."""

    sent_to: str
    masked: str
    expires_in: int
    can_resend_in: int
    dev_code: Optional[str] = None  # Uniquement en dev


@dataclass
class VerifyCodeResult:
    """Résultat de la vérification d'un code."""

    verified_type: str
    verified_at: timezone.datetime
    is_fully_verified: bool
    security_score: int
    security_level: str


class VerificationService:
    """Service de gestion des vérifications."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})

    # =========================================================================
    # ENVOI DE CODE
    # =========================================================================

    def send_code(
        self,
        user: CustomUser,
        verification_type: str,
        purpose: str = VerificationPurpose.ACCOUNT_VERIFICATION,
    ) -> SendCodeResult:
        """
        Envoie un code de vérification.

        Args:
            user: L'utilisateur
            verification_type: 'email' ou 'phone'
            purpose: But de la vérification

        Returns:
            SendCodeResult avec les détails de l'envoi

        Raises:
            NoContactToVerifyError: Si aucun contact de ce type
            AlreadyVerifiedError: Si déjà vérifié
            VerificationCooldownError: Si cooldown actif
        """
        # Vérifier que le contact existe
        if verification_type == VerificationType.EMAIL:
            if not user.email:
                raise NoContactToVerifyError(message="Aucune adresse email configurée")
            if (
                user.email_verified
                and purpose == VerificationPurpose.ACCOUNT_VERIFICATION
            ):
                raise AlreadyVerifiedError(message="L'email est déjà vérifié")
            contact = user.email
            masked = user.masked_email

        elif verification_type == VerificationType.PHONE:
            if not user.phone:
                raise NoContactToVerifyError(
                    message="Aucun numéro de téléphone configuré"
                )
            if (
                user.phone_verified
                and purpose == VerificationPurpose.ACCOUNT_VERIFICATION
            ):
                raise AlreadyVerifiedError(message="Le téléphone est déjà vérifié")
            contact = user.phone
            masked = user.masked_phone

        else:
            raise NoContactToVerifyError(message="Type de vérification invalide")

        # Vérifier le cooldown
        cooldown_remaining = self._check_cooldown(user, verification_type, purpose)
        if cooldown_remaining > 0:
            raise VerificationCooldownError(retry_after=cooldown_remaining)

        # Vérifier la limite journalière
        if self._is_daily_limit_reached(user, verification_type):
            raise VerificationCooldownError(
                message="Limite journalière atteinte. Réessayez demain.",
                retry_after=self._seconds_until_midnight(),
            )

        # Créer le code
        code_obj = VerificationCode.objects.create_code(
            user=user, verification_type=verification_type, purpose=purpose
        )

        # Envoyer la notification
        notification_service = get_notification_service(verification_type)

        if purpose == VerificationPurpose.ACCOUNT_VERIFICATION:
            notification_service.send_verification_code(
                user=user, code=code_obj.code, verification_type=verification_type
            )
        else:
            notification_service.send_password_reset_code(
                user=user, code=code_obj.code, reset_type=verification_type
            )

        logger.info(
            f"Code de vérification envoyé à {user.identifier} "
            f"({verification_type}/{purpose})"
        )

        # Préparer le résultat
        result = SendCodeResult(
            sent_to=contact,
            masked=masked,
            expires_in=code_obj.seconds_until_expiry,
            can_resend_in=self.config.get("VERIFICATION_COOLDOWN_SECONDS", 60),
        )

        # En dev, inclure le code dans la réponse
        if self.config.get("SMS_SHOW_CODE_IN_RESPONSE", False):
            result.dev_code = code_obj.code

        return result

    # =========================================================================
    # CONFIRMATION DE CODE
    # =========================================================================

    @transaction.atomic
    def verify_code(
        self,
        user: CustomUser,
        code: str,
        verification_type: str,
        purpose: str = VerificationPurpose.ACCOUNT_VERIFICATION,
    ) -> VerifyCodeResult:
        """
        Vérifie un code.

        Args:
            user: L'utilisateur
            code: Le code à vérifier
            verification_type: 'email' ou 'phone'
            purpose: But de la vérification

        Returns:
            VerifyCodeResult avec le résultat

        Raises:
            VerificationCodeInvalidError: Si code incorrect
            VerificationCodeExpiredError: Si code expiré
            VerificationMaxAttemptsError: Si trop de tentatives
        """
        # Trouver le code actif
        code_obj = (
            VerificationCode.objects.filter(
                user=user, type=verification_type, purpose=purpose, is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not code_obj:
            raise VerificationCodeInvalidError(
                message="Aucun code de vérification actif"
            )

        # Vérifier l'expiration
        if code_obj.is_expired:
            raise VerificationCodeExpiredError()

        # Vérifier les tentatives max
        if code_obj.max_attempts_reached:
            raise VerificationMaxAttemptsError()

        # Vérifier le code
        if not code_obj.verify(code.strip()):
            remaining = code_obj.remaining_attempts
            if remaining <= 0:
                raise VerificationMaxAttemptsError()
            raise VerificationCodeInvalidError(attempts_remaining=remaining)

        # Marquer comme vérifié
        now = timezone.now()

        if verification_type == VerificationType.EMAIL:
            user.email_verified = True
            user.email_verified_at = now
            user.save(
                update_fields=["email_verified", "email_verified_at", "updated_at"]
            )
        elif verification_type == VerificationType.PHONE:
            user.phone_verified = True
            user.phone_verified_at = now
            user.save(
                update_fields=["phone_verified", "phone_verified_at", "updated_at"]
            )

        logger.info(
            f"Vérification réussie pour {user.identifier} ({verification_type})"
        )

        return VerifyCodeResult(
            verified_type=verification_type,
            verified_at=now,
            is_fully_verified=user.is_verified,
            security_score=user.security_score,
            security_level=user.security_level,
        )

    # =========================================================================
    # STATUT
    # =========================================================================

    def get_verification_status(self, user: CustomUser) -> dict:
        """Retourne le statut de vérification du compte."""
        return {
            "is_verified": user.is_verified,
            "email": {
                "exists": bool(user.email),
                "value_masked": user.masked_email,
                "verified": user.email_verified,
                "verified_at": (
                    user.email_verified_at.isoformat()
                    if user.email_verified_at
                    else None
                ),
            },
            "phone": {
                "exists": bool(user.phone),
                "value_masked": user.masked_phone,
                "verified": user.phone_verified,
                "verified_at": (
                    user.phone_verified_at.isoformat()
                    if user.phone_verified_at
                    else None
                ),
            },
        }

    # =========================================================================
    # UTILITAIRES
    # =========================================================================

    def _check_cooldown(
        self, user: CustomUser, verification_type: str, purpose: str
    ) -> int:
        """
        Vérifie le cooldown avant un nouvel envoi.

        Returns:
            Nombre de secondes à attendre (0 si pas de cooldown)
        """
        cooldown_seconds = self.config.get("VERIFICATION_COOLDOWN_SECONDS", 60)

        # Trouver le dernier code envoyé
        last_code = (
            VerificationCode.objects.filter(
                user=user, type=verification_type, purpose=purpose
            )
            .order_by("-created_at")
            .first()
        )

        if not last_code:
            return 0

        elapsed = (timezone.now() - last_code.created_at).total_seconds()
        remaining = cooldown_seconds - elapsed

        return max(0, int(remaining))

    def _is_daily_limit_reached(self, user: CustomUser, verification_type: str) -> bool:
        """Vérifie si la limite journalière est atteinte."""
        max_daily = self.config.get("VERIFICATION_MAX_DAILY_REQUESTS", 5)

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        count = VerificationCode.objects.filter(
            user=user, type=verification_type, created_at__gte=today_start
        ).count()

        return count >= max_daily

    def _seconds_until_midnight(self) -> int:
        """Retourne le nombre de secondes jusqu'à minuit."""
        now = timezone.now()
        midnight = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timezone.timedelta(days=1)
        return int((midnight - now).total_seconds())
