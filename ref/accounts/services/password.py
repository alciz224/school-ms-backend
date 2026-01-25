# domain/accounts/services/password.py

"""
Service de gestion des mots de passe.
Gère: réinitialisation, changement.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from domain.accounts.models import CustomUser, VerificationCode
from domain.accounts.constants import VerificationType, VerificationPurpose
from domain.accounts.validators import check_password_strength
from domain.accounts.exceptions import (
    InvalidCredentialsError,
    InvalidCurrentPasswordError,
    WeakPasswordError,
    VerificationCodeInvalidError,
    VerificationCodeExpiredError,
    VerificationMaxAttemptsError,
)

from .verification import VerificationService
from .notifications import get_notification_service

logger = logging.getLogger(__name__)


@dataclass
class PasswordResetRequestResult:
    """Résultat d'une demande de réinitialisation."""

    expires_in: int
    next_step: str


@dataclass
class PasswordResetConfirmResult:
    """Résultat de la confirmation de réinitialisation."""

    success: bool
    can_login: bool


@dataclass
class PasswordChangeResult:
    """Résultat du changement de mot de passe."""

    success: bool
    access_token: str
    refresh_token: str


class PasswordService:
    """Service de gestion des mots de passe."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})
        self.verification_service = VerificationService()

    # =========================================================================
    # RÉINITIALISATION
    # =========================================================================

    def request_reset(self, identifier: str) -> PasswordResetRequestResult:
        """
        Demande une réinitialisation de mot de passe.

        Toujours retourne succès pour éviter l'énumération des comptes.

        Args:
            identifier: Email ou téléphone

        Returns:
            PasswordResetRequestResult
        """
        identifier = identifier.strip()
        expiry_minutes = self.config.get("VERIFICATION_CODE_EXPIRY_MINUTES", 10)

        # Chercher l'utilisateur (sans révéler s'il existe)
        user = CustomUser.objects.get_by_identifier(identifier)

        if user and user.is_active:
            # Déterminer le meilleur canal
            if user.email_verified:
                self._send_reset_code(user, VerificationType.EMAIL)
            elif user.phone_verified:
                self._send_reset_code(user, VerificationType.PHONE)
            elif user.email:
                self._send_reset_code(user, VerificationType.EMAIL)
            elif user.phone:
                self._send_reset_code(user, VerificationType.PHONE)

        # Toujours la même réponse
        return PasswordResetRequestResult(
            expires_in=expiry_minutes * 60, next_step="check_email_or_phone"
        )

    def _send_reset_code(self, user: CustomUser, reset_type: str):
        """Envoie le code de réinitialisation."""
        try:
            # Créer le code
            code_obj = VerificationCode.objects.create_code(
                user=user,
                verification_type=reset_type,
                purpose=VerificationPurpose.PASSWORD_RESET,
            )

            # Envoyer la notification
            notification_service = get_notification_service(reset_type)
            notification_service.send_password_reset_code(
                user=user, code=code_obj.code, reset_type=reset_type
            )

            logger.info(
                f"Code de réinitialisation envoyé à {user.identifier} ({reset_type})"
            )

        except Exception as e:
            logger.error(f"Erreur envoi code reset: {e}")

    @transaction.atomic
    def confirm_reset(
        self, identifier: str, code: str, new_password: str
    ) -> PasswordResetConfirmResult:
        """
        Confirme la réinitialisation du mot de passe.

        Args:
            identifier: Email ou téléphone
            code: Code de vérification
            new_password: Nouveau mot de passe

        Returns:
            PasswordResetConfirmResult

        Raises:
            InvalidCredentialsError: Si utilisateur non trouvé
            VerificationCodeInvalidError: Si code incorrect
            VerificationCodeExpiredError: Si code expiré
            WeakPasswordError: Si mot de passe trop faible
        """
        identifier = identifier.strip()

        # Trouver l'utilisateur
        user = CustomUser.objects.get_by_identifier(identifier)
        if not user:
            raise InvalidCredentialsError(
                message="Aucun compte trouvé avec cet identifiant"
            )

        # Valider le nouveau mot de passe
        password_check = check_password_strength(new_password)
        if not password_check["is_strong"]:
            raise WeakPasswordError(issues=password_check["issues"])

        # Trouver et vérifier le code
        code_obj = (
            VerificationCode.objects.filter(
                user=user, purpose=VerificationPurpose.PASSWORD_RESET, is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not code_obj:
            raise VerificationCodeInvalidError(
                message="Aucun code de réinitialisation actif"
            )

        if code_obj.is_expired:
            raise VerificationCodeExpiredError()

        if code_obj.max_attempts_reached:
            raise VerificationMaxAttemptsError()

        if not code_obj.verify(code.strip()):
            remaining = code_obj.remaining_attempts
            if remaining <= 0:
                raise VerificationMaxAttemptsError()
            raise VerificationCodeInvalidError(attempts_remaining=remaining)

        # Changer le mot de passe
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        logger.info(f"Mot de passe réinitialisé pour {user.identifier}")

        return PasswordResetConfirmResult(success=True, can_login=True)

    # =========================================================================
    # CHANGEMENT (UTILISATEUR CONNECTÉ)
    # =========================================================================

    @transaction.atomic
    def change_password(
        self, user: CustomUser, current_password: str, new_password: str
    ) -> PasswordChangeResult:
        """
        Change le mot de passe d'un utilisateur connecté.

        Args:
            user: L'utilisateur
            current_password: Mot de passe actuel
            new_password: Nouveau mot de passe

        Returns:
            PasswordChangeResult avec nouveaux tokens

        Raises:
            InvalidCurrentPasswordError: Si mot de passe actuel incorrect
            WeakPasswordError: Si nouveau mot de passe trop faible
        """
        # Vérifier le mot de passe actuel
        if not user.check_password(current_password):
            raise InvalidCurrentPasswordError()

        # Valider le nouveau mot de passe
        password_check = check_password_strength(new_password)
        if not password_check["is_strong"]:
            raise WeakPasswordError(issues=password_check["issues"])

        # Changer le mot de passe
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        # Générer de nouveaux tokens (invalide les anciens)
        refresh = RefreshToken.for_user(user)

        logger.info(f"Mot de passe changé pour {user.identifier}")

        return PasswordChangeResult(
            success=True,
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
        )
