# domain/accounts/services/auth.py

"""
Service d'authentification.
Gère: inscription, connexion, déconnexion.
"""

import logging
from typing import Tuple, Optional
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from domain.accounts.models import CustomUser, LoginAttempt, VerificationCode
from domain.accounts.constants import VerificationType, VerificationPurpose
from domain.accounts.validators import validate_phone_number, check_password_strength
from domain.accounts.exceptions import (
    InvalidCredentialsError,
    AccountDisabledError,
    AccountLockedError,
    EmailAlreadyExistsError,
    PhoneAlreadyExistsError,
    ValidationError,
    WeakPasswordError,
)

from .notifications import get_notification_service

logger = logging.getLogger(__name__)


@dataclass
class TokenPair:
    """Paire de tokens JWT."""

    access: str
    refresh: str


@dataclass
class AuthResult:
    """Résultat d'une authentification."""

    user: CustomUser
    tokens: TokenPair
    requires_verification: bool
    verification_sent_to: Optional[str] = None


class AuthService:
    """Service d'authentification."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})

    # =========================================================================
    # INSCRIPTION
    # =========================================================================

    @transaction.atomic
    def register(
        self,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        password: str = None,
        first_name: str = None,
        last_name: str = None,
        request_meta: dict = None,
    ) -> AuthResult:
        """
        Inscrit un nouvel utilisateur.

        Args:
            email: Adresse email (optionnel si phone fourni)
            phone: Numéro de téléphone (optionnel si email fourni)
            password: Mot de passe
            first_name: Prénom
            last_name: Nom
            request_meta: Métadonnées de la requête (IP, user-agent)

        Returns:
            AuthResult avec user, tokens et statut de vérification

        Raises:
            ValidationError: Si données invalides
            EmailAlreadyExistsError: Si email déjà utilisé
            PhoneAlreadyExistsError: Si téléphone déjà utilisé
            WeakPasswordError: Si mot de passe trop faible
        """
        # Validation: au moins un identifiant
        if not email and not phone:
            raise ValidationError(
                message="Un email ou un numéro de téléphone est requis",
                field_errors={
                    "email": ["Email ou téléphone requis"],
                    "phone": ["Email ou téléphone requis"],
                },
            )

        # Valider le mot de passe
        password_check = check_password_strength(password)
        if not password_check["is_strong"]:
            raise WeakPasswordError(issues=password_check["issues"])

        # Vérifier unicité email
        if email:
            email = email.lower().strip()
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise EmailAlreadyExistsError()

        # Vérifier unicité téléphone
        if phone:
            phone = validate_phone_number(phone)
            if CustomUser.objects.filter(phone=phone).exists():
                raise PhoneAlreadyExistsError()

        # Créer l'utilisateur
        user = CustomUser.objects.create_user(
            email=email,
            phone=phone,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
        )

        # Générer les tokens
        tokens = self._generate_tokens(user)

        # Envoyer le code de vérification
        verification_sent_to = self._send_initial_verification(user)

        logger.info(f"Nouvel utilisateur inscrit: {user.identifier}")

        return AuthResult(
            user=user,
            tokens=tokens,
            requires_verification=not user.is_verified,
            verification_sent_to=verification_sent_to,
        )

    def _send_initial_verification(self, user: CustomUser) -> Optional[str]:
        """Envoie le premier code de vérification."""
        from .verification import VerificationService

        verification_service = VerificationService()

        # Priorité à l'email (gratuit)
        if user.email:
            try:
                verification_service.send_code(user, "email")
                return "email"
            except Exception as e:
                logger.warning(f"Échec envoi vérification email: {e}")

        # Sinon téléphone
        if user.phone:
            try:
                verification_service.send_code(user, "phone")
                return "phone"
            except Exception as e:
                logger.warning(f"Échec envoi vérification phone: {e}")

        return None

    # =========================================================================
    # CONNEXION
    # =========================================================================

    def login(
        self,
        identifier: str,
        password: str,
        ip_address: str = None,
        user_agent: str = "",
    ) -> AuthResult:
        """
        Authentifie un utilisateur.

        Args:
            identifier: Email ou téléphone
            password: Mot de passe
            ip_address: Adresse IP du client
            user_agent: User-Agent du navigateur

        Returns:
            AuthResult avec user, tokens et statut de vérification

        Raises:
            InvalidCredentialsError: Si identifiants incorrects
            AccountDisabledError: Si compte désactivé
            AccountLockedError: Si compte verrouillé
        """
        identifier = identifier.strip()

        # Vérifier le verrouillage
        if self._is_locked_out(identifier, ip_address):
            lockout_info = self._get_lockout_info(identifier, ip_address)
            raise AccountLockedError(**lockout_info)

        # Trouver l'utilisateur
        user = CustomUser.objects.get_by_identifier(identifier)

        if not user:
            # Enregistrer la tentative échouée
            self._record_failed_attempt(
                identifier=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                reason="not_found",
            )
            raise InvalidCredentialsError()

        # Vérifier le mot de passe
        if not user.check_password(password):
            self._record_failed_attempt(
                identifier=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user,
                reason="invalid_password",
            )
            raise InvalidCredentialsError()

        # Vérifier si le compte est actif
        if not user.is_active:
            self._record_failed_attempt(
                identifier=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user,
                reason="account_disabled",
            )
            raise AccountDisabledError()

        # Enregistrer la connexion réussie
        self._record_successful_login(
            identifier=identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            user=user,
        )

        # Mettre à jour last_login
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # Générer les tokens
        tokens = self._generate_tokens(user)

        logger.info(f"Connexion réussie: {user.identifier}")

        return AuthResult(
            user=user, tokens=tokens, requires_verification=not user.is_verified
        )

    # =========================================================================
    # DÉCONNEXION
    # =========================================================================

    def logout(self, refresh_token: str) -> bool:
        """
        Déconnecte l'utilisateur en blacklistant le refresh token.

        Args:
            refresh_token: Le refresh token à invalider

        Returns:
            True si déconnexion réussie
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("Déconnexion réussie - token blacklisté")
            return True
        except Exception as e:
            logger.warning(f"Erreur lors de la déconnexion: {e}")
            return False

    # =========================================================================
    # UTILITAIRES
    # =========================================================================

    def _generate_tokens(self, user: CustomUser) -> TokenPair:
        """Génère une paire de tokens JWT."""
        refresh = RefreshToken.for_user(user)
        return TokenPair(access=str(refresh.access_token), refresh=str(refresh))

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """
        Rafraîchit les tokens.

        Args:
            refresh_token: Le refresh token actuel

        Returns:
            Nouvelle paire de tokens
        """
        try:
            refresh = RefreshToken(refresh_token)

            # Créer de nouveaux tokens
            new_tokens = TokenPair(
                access=str(refresh.access_token), refresh=str(refresh)
            )

            # Blacklister l'ancien si rotation activée
            if settings.SIMPLE_JWT.get("ROTATE_REFRESH_TOKENS", False):
                refresh.blacklist()
                new_refresh = RefreshToken.for_user(
                    CustomUser.objects.get(id=refresh.payload["user_id"])
                )
                new_tokens = TokenPair(
                    access=str(new_refresh.access_token), refresh=str(new_refresh)
                )

            return new_tokens

        except Exception as e:
            logger.error(f"Erreur refresh token: {e}")
            raise InvalidCredentialsError(
                message="Token invalide ou expiré", code="AUTH_TOKEN_INVALID"
            )

    # =========================================================================
    # RATE LIMITING / VERROUILLAGE
    # =========================================================================

    def _is_locked_out(self, identifier: str, ip_address: str) -> bool:
        """Vérifie si l'utilisateur/IP est verrouillé."""
        return LoginAttempt.is_locked_out(identifier=identifier, ip_address=ip_address)

    def _get_lockout_info(self, identifier: str, ip_address: str) -> dict:
        """Récupère les infos de verrouillage."""
        lockout_minutes = self.config.get("LOGIN_LOCKOUT_MINUTES", 30)

        # Trouver la dernière tentative
        last_attempt = (
            LoginAttempt.objects.filter(identifier=identifier, success=False)
            .order_by("-created_at")
            .first()
        )

        if last_attempt:
            locked_until = last_attempt.created_at + timezone.timedelta(
                minutes=lockout_minutes
            )
            remaining = (locked_until - timezone.now()).total_seconds() / 60

            return {
                "locked_until": locked_until,
                "remaining_minutes": max(0, int(remaining)),
            }

        return {"locked_until": None, "remaining_minutes": 0}

    def _record_failed_attempt(
        self,
        identifier: str,
        ip_address: str,
        user_agent: str,
        user: CustomUser = None,
        reason: str = "invalid_credentials",
    ):
        """Enregistre une tentative de connexion échouée."""
        LoginAttempt.record(
            identifier=identifier,
            ip_address=ip_address or "0.0.0.0",
            user=user,
            success=False,
            failure_reason=reason,
            user_agent=user_agent,
        )

    def _record_successful_login(
        self, identifier: str, ip_address: str, user_agent: str, user: CustomUser
    ):
        """Enregistre une connexion réussie."""
        LoginAttempt.record(
            identifier=identifier,
            ip_address=ip_address or "0.0.0.0",
            user=user,
            success=True,
            user_agent=user_agent,
        )
