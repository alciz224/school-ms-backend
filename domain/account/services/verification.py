"""
Verification service.
Handles: code sending, confirmation, status.
"""

import logging
from typing import Optional
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from domain.account.models import CustomUser, VerificationCode
from domain.account.constants import VerificationType, VerificationPurpose
from domain.account.exceptions import (
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
    """Code sending result."""

    sent_to: str
    masked: str
    expires_in: int
    can_resend_in: int
    dev_code: Optional[str] = None  # Only in dev


@dataclass
class VerifyCodeResult:
    """Code verification result."""

    verified_type: str
    verified_at: timezone.datetime
    is_fully_verified: bool
    security_score: int
    security_level: str


class VerificationService:
    """Verification management service."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})

    # =========================================================================
    # CODE SENDING
    # =========================================================================

    def send_code(
        self,
        user: CustomUser,
        verification_type: str,
        purpose: str = VerificationPurpose.ACCOUNT_VERIFICATION,
    ) -> SendCodeResult:
        """
        Send a verification code.

        Args:
            user: The user
            verification_type: 'email' or 'phone'
            purpose: Purpose of verification

        Returns:
            SendCodeResult with sending details

        Raises:
            NoContactToVerifyError: If no contact of this type
            AlreadyVerifiedError: If already verified
            VerificationCooldownError: If cooldown active
        """
        # Check contact exists
        if verification_type == VerificationType.EMAIL:
            if not user.email:
                raise NoContactToVerifyError(message="No email address configured")
            if (
                user.email_verified
                and purpose == VerificationPurpose.ACCOUNT_VERIFICATION
            ):
                raise AlreadyVerifiedError(message="Email is already verified")
            contact = user.email
            masked = user.masked_email

        elif verification_type == VerificationType.PHONE:
            if not user.phone:
                raise NoContactToVerifyError(
                    message="No phone number configured"
                )
            if (
                user.phone_verified
                and purpose == VerificationPurpose.ACCOUNT_VERIFICATION
            ):
                raise AlreadyVerifiedError(message="Phone is already verified")
            contact = user.phone
            masked = user.masked_phone

        else:
            raise NoContactToVerifyError(message="Invalid verification type")

        # Check cooldown
        cooldown_remaining = self._check_cooldown(user, verification_type, purpose)
        if cooldown_remaining > 0:
            raise VerificationCooldownError(retry_after=cooldown_remaining)

        # Check daily limit
        if self._is_daily_limit_reached(user, verification_type):
            raise VerificationCooldownError(
                message="Daily limit reached. Try again tomorrow.",
                retry_after=self._seconds_until_midnight(),
            )

        # Create code
        code_obj = VerificationCode.objects.create_code(
            user=user, verification_type=verification_type, purpose=purpose
        )

        # Send notification
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
            f"Verification code sent to {user.identifier} "
            f"({verification_type}/{purpose})"
        )

        # Prepare result
        result = SendCodeResult(
            sent_to=contact,
            masked=masked,
            expires_in=code_obj.seconds_until_expiry,
            can_resend_in=self.config.get("VERIFICATION_COOLDOWN_SECONDS", 60),
        )

        # In dev, include code in response
        if settings.DEBUG:
            result.dev_code = code_obj.code

        return result

    # =========================================================================
    # CODE CONFIRMATION
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
        Verify a code.

        Args:
            user: The user
            code: The code to verify
            verification_type: 'email' or 'phone'
            purpose: Purpose of verification

        Returns:
            VerifyCodeResult with result

        Raises:
            VerificationCodeInvalidError: If code incorrect
            VerificationCodeExpiredError: If code expired
            VerificationMaxAttemptsError: If too many attempts
        """
        # Find active code
        code_obj = (
            VerificationCode.objects.filter(
                user=user, type=verification_type, purpose=purpose, is_used=False
            )
            .order_by("-created_at")
            .first()
        )

        if not code_obj:
            raise VerificationCodeInvalidError(
                message="No active verification code"
            )

        # Check expiration
        if code_obj.is_expired:
            raise VerificationCodeExpiredError()

        # Check max attempts
        if code_obj.max_attempts_reached:
            raise VerificationMaxAttemptsError()

        # Verify code
        if not code_obj.verify(code.strip()):
            remaining = code_obj.remaining_attempts
            if remaining <= 0:
                raise VerificationMaxAttemptsError()
            raise VerificationCodeInvalidError(attempts_remaining=remaining)

        # Mark as verified
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
            f"Verification successful for {user.identifier} ({verification_type})"
        )

        return VerifyCodeResult(
            verified_type=verification_type,
            verified_at=now,
            is_fully_verified=user.is_verified,
            security_score=user.security_score,
            security_level=user.security_level,
        )

    # =========================================================================
    # STATUS
    # =========================================================================

    def get_verification_status(self, user: CustomUser) -> dict:
        """Return account verification status."""
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
    # UTILITIES
    # =========================================================================

    def _check_cooldown(
        self, user: CustomUser, verification_type: str, purpose: str
    ) -> int:
        """
        Check cooldown before new send.

        Returns:
            Seconds to wait (0 if no cooldown)
        """
        cooldown_seconds = self.config.get("VERIFICATION_COOLDOWN_SECONDS", 60)

        # Find last code sent
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
        """Check if daily limit is reached."""
        max_daily = self.config.get("VERIFICATION_MAX_DAILY_REQUESTS", 5)

        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)

        count = VerificationCode.objects.filter(
            user=user, type=verification_type, created_at__gte=today_start
        ).count()

        return count >= max_daily

    def _seconds_until_midnight(self) -> int:
        """Return seconds until midnight."""
        now = timezone.now()
        midnight = now.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) + timezone.timedelta(days=1)
        return int((midnight - now).total_seconds())
