"""
Password management service.
Handles: reset, change.
"""

import logging
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from rest_framework_simplejwt.tokens import RefreshToken

from domain.account.models import CustomUser, VerificationCode
from domain.account.constants import VerificationType, VerificationPurpose
from domain.account.validators import check_password_strength
from domain.account.exceptions import (
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
    """Password reset request result."""

    expires_in: int
    next_step: str


@dataclass
class PasswordResetConfirmResult:
    """Password reset confirmation result."""

    success: bool
    can_login: bool


@dataclass
class PasswordChangeResult:
    """Password change result."""

    success: bool
    access_token: str
    refresh_token: str


class PasswordService:
    """Password management service."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})
        self.verification_service = VerificationService()

    # =========================================================================
    # RESET
    # =========================================================================

    def request_reset(self, identifier: str) -> PasswordResetRequestResult:
        """
        Request a password reset.

        Always returns success to prevent account enumeration.

        Args:
            identifier: Email or phone

        Returns:
            PasswordResetRequestResult
        """
        identifier = identifier.strip()
        expiry_minutes = self.config.get("VERIFICATION_CODE_EXPIRY_MINUTES", 10)

        # Find user (without revealing if they exist)
        user = CustomUser.objects.get_by_identifier(identifier)

        if user and user.is_active:
            # Determine best channel
            if user.email_verified:
                self._send_reset_code(user, VerificationType.EMAIL)
            elif user.phone_verified:
                self._send_reset_code(user, VerificationType.PHONE)
            elif user.email:
                self._send_reset_code(user, VerificationType.EMAIL)
            elif user.phone:
                self._send_reset_code(user, VerificationType.PHONE)

        # Always same response
        return PasswordResetRequestResult(
            expires_in=expiry_minutes * 60, next_step="check_email_or_phone"
        )

    def _send_reset_code(self, user: CustomUser, reset_type: str):
        """Send reset code."""
        try:
            # Create code
            code_obj = VerificationCode.objects.create_code(
                user=user,
                verification_type=reset_type,
                purpose=VerificationPurpose.PASSWORD_RESET,
            )

            # Send notification
            notification_service = get_notification_service(reset_type)
            notification_service.send_password_reset_code(
                user=user, code=code_obj.code, reset_type=reset_type
            )

            logger.info(
                f"Reset code sent to {user.identifier} ({reset_type})"
            )

        except Exception as e:
            logger.error(f"Failed to send reset code: {e}")

    @transaction.atomic
    def confirm_reset(
        self, identifier: str, code: str, new_password: str
    ) -> PasswordResetConfirmResult:
        """
        Confirm password reset.

        Args:
            identifier: Email or phone
            code: Verification code
            new_password: New password

        Returns:
            PasswordResetConfirmResult

        Raises:
            InvalidCredentialsError: If user not found
            VerificationCodeInvalidError: If code incorrect
            VerificationCodeExpiredError: If code expired
            WeakPasswordError: If password too weak
        """
        identifier = identifier.strip()

        # Find user
        user = CustomUser.objects.get_by_identifier(identifier)
        if not user:
            raise InvalidCredentialsError(
                message="No account found with this identifier"
            )

        # Validate new password
        password_check = check_password_strength(new_password)
        if not password_check["is_strong"]:
            raise WeakPasswordError(issues=password_check["issues"])

        # Find and verify code
        code_obj = (
            VerificationCode.objects.filter(
                user=user, purpose=VerificationPurpose.PASSWORD_RESET, is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not code_obj:
            raise VerificationCodeInvalidError(
                message="No active reset code"
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

        # Change password
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        logger.info(f"Password reset for {user.identifier}")

        return PasswordResetConfirmResult(success=True, can_login=True)

    # =========================================================================
    # CHANGE (LOGGED IN USER)
    # =========================================================================

    @transaction.atomic
    def change_password(
        self, user: CustomUser, current_password: str, new_password: str
    ) -> PasswordChangeResult:
        """
        Change password for logged in user.

        Args:
            user: The user
            current_password: Current password
            new_password: New password

        Returns:
            PasswordChangeResult with new tokens

        Raises:
            InvalidCurrentPasswordError: If current password incorrect
            WeakPasswordError: If new password too weak
        """
        # Verify current password
        if not user.check_password(current_password):
            raise InvalidCurrentPasswordError()

        # Validate new password
        password_check = check_password_strength(new_password)
        if not password_check["is_strong"]:
            raise WeakPasswordError(issues=password_check["issues"])

        # Change password
        user.set_password(new_password)
        user.save(update_fields=["password", "updated_at"])

        # Generate new tokens (invalidates old ones)
        refresh = RefreshToken.for_user(user)

        logger.info(f"Password changed for {user.identifier}")

        return PasswordChangeResult(
            success=True,
            access_token=str(refresh.access_token),
            refresh_token=str(refresh),
        )
