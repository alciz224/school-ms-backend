"""
Email notification service.
"""

import logging
from typing import TYPE_CHECKING
from django.conf import settings
from django.core.mail import send_mail

from .base import BaseNotificationService

if TYPE_CHECKING:
    from domain.account.models import CustomUser

logger = logging.getLogger(__name__)


class EmailNotificationService(BaseNotificationService):
    """Email sending service."""

    def __init__(self):
        self.from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@school.com")

    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        """Send verification code via email."""
        if verification_type != "email" or not user.email:
            return False

        subject = "Your verification code"

        expiry_minutes = getattr(settings, "ACCOUNTS_CONFIG", {}).get(
            "VERIFICATION_CODE_EXPIRY_MINUTES", 10
        )

        message = (
            f"Hello {user.first_name},\n\n"
            f"Your verification code is: {code}\n\n"
            f"This code expires in {expiry_minutes} minutes.\n\n"
            f"If you did not request this code, please ignore this email.\n\n"
            f"Best regards,\n"
            f"The School Management System Team"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Verification email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send email to {user.email}: {e}")
            return False

    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        """Send password reset code via email."""
        if reset_type != "email" or not user.email:
            return False

        subject = "Password reset request"

        expiry_minutes = getattr(settings, "ACCOUNTS_CONFIG", {}).get(
            "VERIFICATION_CODE_EXPIRY_MINUTES", 10
        )

        message = (
            f"Hello {user.first_name},\n\n"
            f"You have requested a password reset.\n\n"
            f"Your reset code is: {code}\n\n"
            f"This code expires in {expiry_minutes} minutes.\n\n"
            f"If you did not make this request, "
            f"please secure your account immediately.\n\n"
            f"Best regards,\n"
            f"The School Management System Team"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Password reset email sent to {user.email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send reset email to {user.email}: {e}")
            return False

    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        """Send suspicious login alert."""
        if not user.email:
            return False

        subject = "New login to your account"

        message = (
            f"Hello {user.first_name},\n\n"
            f"A new login was detected on your account.\n\n"
            f"Details:\n"
            f"- IP Address: {ip_address}\n"
            f"- Device: {user_agent[:100]}\n\n"
            f"If this was not you, please change your password immediately.\n\n"
            f"Best regards,\n"
            f"The School Management System Team"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
            return True
        except Exception as e:
            logger.error(f"Failed to send login alert to {user.email}: {e}")
            return False
