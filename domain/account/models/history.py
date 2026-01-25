"""
Models for history and tracking.
"""

import uuid
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.conf import settings

from ..constants import PhoneRemovalReason, LoginFailureReason


class PhoneHistory(models.Model):
    """
    History of user phone numbers.

    Useful for:
        - Change traceability
        - Recovery if new number is lost
        - Security (detect suspicious patterns)
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="phone_history",
        verbose_name=_("User"),
    )

    phone = models.CharField(verbose_name=_("Phone number"), max_length=20)

    verified = models.BooleanField(
        verbose_name=_("Was verified"),
        default=False,
        help_text=_("Was the number verified before removal?"),
    )

    added_at = models.DateTimeField(
        verbose_name=_("Added at"),
        help_text=_("When the number was added to the account."),
    )

    removed_at = models.DateTimeField(
        verbose_name=_("Removed at"), default=timezone.now
    )

    reason = models.CharField(
        verbose_name=_("Reason"),
        max_length=20,
        choices=PhoneRemovalReason.choices,
        default=PhoneRemovalReason.CHANGED,
    )

    class Meta:
        verbose_name = _("Phone history")
        verbose_name_plural = _("Phone histories")
        ordering = ["-removed_at"]

        indexes = [
            models.Index(fields=["user", "removed_at"]),
            models.Index(fields=["phone"]),
        ]

    def __str__(self):
        return f"{self.user} - {self.phone} ({self.reason})"

    def save(self, *args, **kwargs):
        # If added_at is not set, use registration date
        if not self.added_at:
            self.added_at = self.user.date_joined
        super().save(*args, **kwargs)


class LoginAttempt(models.Model):
    """
    Record login attempts.

    Useful for:
        - Rate limiting
        - Brute-force detection
        - Security audit
        - Alert user of suspicious activity
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    identifier = models.CharField(
        verbose_name=_("Identifier used"),
        max_length=255,
        help_text=_("Email or phone used for the attempt."),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="login_attempts",
        verbose_name=_("User"),
        help_text=_("NULL if account doesn't exist."),
    )

    ip_address = models.GenericIPAddressField(verbose_name=_("IP address"))

    user_agent = models.TextField(
        verbose_name=_("User Agent"), blank=True, default=""
    )

    success = models.BooleanField(verbose_name=_("Successful"), default=False)

    failure_reason = models.CharField(
        verbose_name=_("Failure reason"),
        max_length=30,
        choices=LoginFailureReason.choices,
        null=True,
        blank=True,
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date"), auto_now_add=True, db_index=True
    )

    class Meta:
        verbose_name = _("Login attempt")
        verbose_name_plural = _("Login attempts")
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
        Record a login attempt.
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
        Count recent failures for an identifier or IP.
        """
        since = timezone.now() - timezone.timedelta(minutes=minutes)

        queryset = cls.objects.filter(success=False, created_at__gte=since)

        if identifier:
            queryset = queryset.filter(identifier=identifier)

        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)

        return queryset.count()

    @classmethod
    def is_locked_out(
        cls, identifier: str = None, ip_address: str = None
    ) -> bool:
        """
        Check if the identifier or IP is locked out.
        """
        config = getattr(settings, "ACCOUNTS_CONFIG", {})
        max_attempts = config.get("LOGIN_MAX_ATTEMPTS", 5)
        lockout_minutes = config.get("LOGIN_LOCKOUT_MINUTES", 30)

        failures = cls.get_recent_failures(
            identifier=identifier, ip_address=ip_address, minutes=lockout_minutes
        )

        return failures >= max_attempts
