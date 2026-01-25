"""
SMS notification service.
"""

import logging
from typing import TYPE_CHECKING
from django.conf import settings

from .base import BaseNotificationService

if TYPE_CHECKING:
    from domain.account.models import CustomUser

logger = logging.getLogger(__name__)


class SMSNotificationService(BaseNotificationService):
    """
    SMS sending service.
    Prepared for Twilio, Africa's Talking, etc.
    """

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})
        self.enabled = self.config.get("SMS_ENABLED", False)
        self.backend = self.config.get("SMS_BACKEND", "console")

    def _send_sms(self, phone: str, message: str) -> bool:
        """Send SMS via configured backend."""
        if not self.enabled:
            logger.warning(f"SMS disabled. Message for {phone}: {message[:50]}...")
            return False

        # TODO: Implement real backends (Twilio, Africa's Talking)
        logger.info(f"SMS sent to {phone}: {message[:50]}...")
        return True

    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        if verification_type not in ("phone", "sms") or not user.phone:
            return False

        message = f"School System - Your code: {code}. Valid for 10 min."
        return self._send_sms(user.phone, message)

    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        if reset_type not in ("phone", "sms") or not user.phone:
            return False

        message = f"School System - Reset code: {code}. Valid for 10 min."
        return self._send_sms(user.phone, message)

    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        if not user.phone:
            return False

        message = f"School System - New login from {ip_address}."
        return self._send_sms(user.phone, message)
