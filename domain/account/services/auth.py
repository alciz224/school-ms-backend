"""
Authentication service.
Handles: registration, login, logout.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from domain.account.models import CustomUser, LoginAttempt
from domain.account.constants import VerificationType, VerificationPurpose
from domain.account.validators import validate_phone_number, check_password_strength
from domain.account.exceptions import (
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
    """JWT token pair."""

    access: str
    refresh: str


@dataclass
class AuthResult:
    """Authentication result."""

    user: CustomUser
    tokens: TokenPair
    requires_verification: bool
    verification_sent_to: Optional[str] = None


class AuthService:
    """Authentication service."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})

    # =========================================================================
    # REGISTRATION
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
        Register a new user.

        Args:
            email: Email address (optional if phone provided)
            phone: Phone number (optional if email provided)
            password: Password
            first_name: First name
            last_name: Last name
            request_meta: Request metadata (IP, user-agent)

        Returns:
            AuthResult with user, tokens and verification status

        Raises:
            ValidationError: If data is invalid
            EmailAlreadyExistsError: If email already in use
            PhoneAlreadyExistsError: If phone already in use
            WeakPasswordError: If password too weak
        """
        # Validation: at least one identifier
        if not email and not phone:
            raise ValidationError(
                message="An email or phone number is required",
                field_errors={
                    "email": ["Email or phone required"],
                    "phone": ["Email or phone required"],
                },
            )

        # Validate password
        password_check = check_password_strength(password)
        if not password_check["is_strong"]:
            raise WeakPasswordError(issues=password_check["issues"])

        # Check email uniqueness
        if email:
            # Normalize email using Django's normalization (lowercase domain only)
            email = CustomUser.objects.normalize_email(email.strip())
            if CustomUser.objects.filter(email__iexact=email).exists():
                raise EmailAlreadyExistsError()

        # Check phone uniqueness
        if phone:
            phone = validate_phone_number(phone)
            if CustomUser.objects.filter(phone=phone).exists():
                raise PhoneAlreadyExistsError()

        # Create user
        user = CustomUser.objects.create_user(
            email=email,
            phone=phone,
            password=password,
            first_name=first_name.strip(),
            last_name=last_name.strip(),
        )

        # Generate tokens
        tokens = self._generate_tokens(user)

        # Send verification code
        verification_sent_to = self._send_initial_verification(user)

        logger.info(f"New user registered: {user.identifier}")

        return AuthResult(
            user=user,
            tokens=tokens,
            requires_verification=not user.is_verified,
            verification_sent_to=verification_sent_to,
        )

    def _send_initial_verification(self, user: CustomUser) -> Optional[str]:
        """Send initial verification code."""
        from .verification import VerificationService

        verification_service = VerificationService()

        # Priority to email (free)
        if user.email:
            try:
                verification_service.send_code(user, "email")
                return "email"
            except Exception as e:
                logger.warning(f"Failed to send email verification: {e}")

        # Otherwise phone
        if user.phone:
            try:
                verification_service.send_code(user, "phone")
                return "phone"
            except Exception as e:
                logger.warning(f"Failed to send phone verification: {e}")

        return None

    # =========================================================================
    # LOGIN
    # =========================================================================

    def login(
        self,
        identifier: str,
        password: str,
        ip_address: str = None,
        user_agent: str = "",
    ) -> AuthResult:
        """
        Authenticate a user.

        Args:
            identifier: Email or phone
            password: Password
            ip_address: Client IP address
            user_agent: Browser user-agent

        Returns:
            AuthResult with user, tokens and verification status

        Raises:
            InvalidCredentialsError: If credentials are incorrect
            AccountDisabledError: If account is disabled
            AccountLockedError: If account is locked
        """
        identifier = identifier.strip()

        # Check lockout
        if self._is_locked_out(identifier, ip_address):
            lockout_info = self._get_lockout_info(identifier, ip_address)
            raise AccountLockedError(**lockout_info)

        # Find user
        user = CustomUser.objects.get_by_identifier(identifier)

        if not user:
            # Record failed attempt
            self._record_failed_attempt(
                identifier=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                reason="not_found",
            )
            raise InvalidCredentialsError()

        # Verify password
        if not user.check_password(password):
            self._record_failed_attempt(
                identifier=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user,
                reason="invalid_password",
            )
            raise InvalidCredentialsError()

        # Check if account is active
        if not user.is_active:
            self._record_failed_attempt(
                identifier=identifier,
                ip_address=ip_address,
                user_agent=user_agent,
                user=user,
                reason="account_disabled",
            )
            raise AccountDisabledError()

        # Record successful login
        self._record_successful_login(
            identifier=identifier,
            ip_address=ip_address,
            user_agent=user_agent,
            user=user,
        )

        # Update last_login
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])

        # Generate tokens
        tokens = self._generate_tokens(user)

        logger.info(f"Successful login: {user.identifier}")

        return AuthResult(
            user=user, tokens=tokens, requires_verification=not user.is_verified
        )

    # =========================================================================
    # LOGOUT
    # =========================================================================

    def logout(self, refresh_token: str) -> bool:
        """
        Logout user by blacklisting refresh token.

        Args:
            refresh_token: The refresh token to invalidate

        Returns:
            True if logout successful
        """
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            logger.info("Logout successful - token blacklisted")
            return True
        except Exception as e:
            logger.warning(f"Logout error: {e}")
            return False

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def _generate_tokens(self, user: CustomUser) -> TokenPair:
        """Generate JWT token pair."""
        refresh = RefreshToken.for_user(user)
        return TokenPair(access=str(refresh.access_token), refresh=str(refresh))

    def refresh_tokens(self, refresh_token: str) -> TokenPair:
        """
        Refresh tokens.

        Args:
            refresh_token: Current refresh token

        Returns:
            New token pair
        """
        try:
            refresh = RefreshToken(refresh_token)

            # Create new tokens
            new_tokens = TokenPair(
                access=str(refresh.access_token), refresh=str(refresh)
            )

            # Blacklist old if rotation enabled
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
            logger.error(f"Token refresh error: {e}")
            raise InvalidCredentialsError(
                message="Invalid or expired token", code="AUTH_TOKEN_INVALID"
            )

    # =========================================================================
    # RATE LIMITING / LOCKOUT
    # =========================================================================

    def _is_locked_out(self, identifier: str, ip_address: str) -> bool:
        """Check if user/IP is locked out."""
        return LoginAttempt.is_locked_out(identifier=identifier, ip_address=ip_address)

    def _get_lockout_info(self, identifier: str, ip_address: str) -> dict:
        """Get lockout information."""
        lockout_minutes = self.config.get("LOGIN_LOCKOUT_MINUTES", 30)

        # Find last attempt
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
        """Record a failed login attempt."""
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
        """Record a successful login."""
        LoginAttempt.record(
            identifier=identifier,
            ip_address=ip_address or "0.0.0.0",
            user=user,
            success=True,
            user_agent=user_agent,
        )
