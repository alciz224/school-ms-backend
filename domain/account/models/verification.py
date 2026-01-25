"""
Models for verification code management.
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
    """Generate a 6-digit verification code."""
    return "".join(secrets.choice("0123456789") for _ in range(6))


def get_code_expiry() -> timezone.datetime:
    """Return the default expiry date."""
    config = getattr(settings, "ACCOUNTS_CONFIG", {})
    minutes = config.get("VERIFICATION_CODE_EXPIRY_MINUTES", 10)
    return timezone.now() + timedelta(minutes=minutes)


class VerificationCodeManager(models.Manager):
    """Manager for verification codes."""

    def create_code(
        self, user, verification_type: str, purpose: str
    ) -> "VerificationCode":
        """
        Create a new verification code.

        Invalidates old codes of the same type/purpose.
        """
        # Invalidate old codes
        self.filter(
            user=user, type=verification_type, purpose=purpose, is_used=False
        ).update(is_used=True)

        # Create new one
        return self.create(user=user, type=verification_type, purpose=purpose)

    def get_valid_code(
        self, user, code: str, verification_type: str, purpose: str
    ) -> "VerificationCode | None":
        """
        Get a valid code if it exists.
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
        Delete expired codes.
        Returns the number of deleted codes.
        """
        result = self.filter(
            models.Q(expires_at__lt=timezone.now()) | models.Q(is_used=True)
        ).delete()
        return result[0]


class VerificationCode(models.Model):
    """
    Temporary verification code.

    Used for:
        - Account verification (email/phone)
        - Password reset
        - OTP login
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="verification_codes",
        verbose_name=_("User"),
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
        verbose_name=_("Purpose"), max_length=20, choices=VerificationPurpose.choices
    )

    expires_at = models.DateTimeField(
        verbose_name=_("Expires at"), default=get_code_expiry
    )

    attempts = models.PositiveSmallIntegerField(verbose_name=_("Attempts"), default=0)

    is_used = models.BooleanField(verbose_name=_("Used"), default=False)

    created_at = models.DateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
    )

    objects = VerificationCodeManager()

    class Meta:
        verbose_name = _("Verification code")
        verbose_name_plural = _("Verification codes")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user", "type", "purpose", "is_used"]),
            models.Index(fields=["expires_at"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.type}/{self.purpose} - {'Used' if self.is_used else 'Active'}"

    @property
    def is_expired(self) -> bool:
        """Check if the code is expired."""
        return timezone.now() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if the code is still valid."""
        return not self.is_used and not self.is_expired

    @property
    def max_attempts_reached(self) -> bool:
        """Check if max attempts have been reached."""
        config = getattr(settings, "ACCOUNTS_CONFIG", {})
        max_attempts = config.get("VERIFICATION_MAX_ATTEMPTS", 3)
        return self.attempts >= max_attempts

    @property
    def remaining_attempts(self) -> int:
        """Number of remaining attempts."""
        config = getattr(settings, "ACCOUNTS_CONFIG", {})
        max_attempts = config.get("VERIFICATION_MAX_ATTEMPTS", 3)
        return max(0, max_attempts - self.attempts)

    @property
    def seconds_until_expiry(self) -> int:
        """Seconds remaining until expiry."""
        if self.is_expired:
            return 0
        delta = self.expires_at - timezone.now()
        return max(0, int(delta.total_seconds()))

    def verify(self, code: str) -> bool:
        """
        Verify the provided code.

        Args:
            code: The code to verify

        Returns:
            True if correct, False otherwise
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
        Regenerate a new code.

        Returns:
            The new code
        """
        self.code = generate_verification_code()
        self.expires_at = get_code_expiry()
        self.attempts = 0
        self.is_used = False
        self.save()
        return self.code
