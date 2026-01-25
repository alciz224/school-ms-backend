"""
Console notification service for development.
Displays messages in console/logs instead of sending them.
"""

import logging
from typing import TYPE_CHECKING

from .base import BaseNotificationService

if TYPE_CHECKING:
    from domain.account.models import CustomUser

logger = logging.getLogger(__name__)


class ConsoleNotificationService(BaseNotificationService):
    """
    Notification service for development.
    Displays messages in the console.
    """

    def _log_notification(self, notification_type: str, recipient: str, message: str):
        """Display notification in the console."""
        separator = "=" * 60
        print(f"\n{separator}")
        print(f"📧 NOTIFICATION ({notification_type.upper()})")
        print(f"📬 Recipient: {recipient}")
        print(f"{separator}")
        print(message)
        print(f"{separator}\n")

        logger.info(f"[{notification_type}] → {recipient}: {message[:50]}...")

    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        """Display verification code in the console."""
        recipient = user.email if verification_type == "email" else user.phone

        if not recipient:
            return False

        message = (
            f"Hello {user.first_name},\n\n"
            f"🔐 Your verification code: {code}\n\n"
            f"This code expires in 10 minutes."
        )

        self._log_notification(verification_type, recipient, message)
        return True

    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        """Display reset code in the console."""
        recipient = user.email if reset_type == "email" else user.phone

        if not recipient:
            return False

        message = (
            f"Hello {user.first_name},\n\n"
            f"🔑 Your reset code: {code}\n\n"
            f"This code expires in 10 minutes."
        )

        self._log_notification(reset_type, recipient, message)
        return True

    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        """Display login alert in the console."""
        recipient = user.email or user.phone

        if not recipient:
            return False

        message = (
            f"Hello {user.first_name},\n\n"
            f"⚠️ New login detected\n"
            f"IP: {ip_address}\n"
            f"Device: {user_agent[:50]}"
        )

        self._log_notification("login_alert", recipient, message)
        return True
