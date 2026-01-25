# domain/accounts/services/notifications/sms.py

import logging
from typing import TYPE_CHECKING
from django.conf import settings

from .base import BaseNotificationService

if TYPE_CHECKING:
    from domain.accounts.models import CustomUser

logger = logging.getLogger(__name__)


class SMSNotificationService(BaseNotificationService):
    """
    Service d'envoi de SMS.
    Préparé pour Twilio, Africa's Talking, etc.
    """

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})
        self.enabled = self.config.get("SMS_ENABLED", False)
        self.backend = self.config.get("SMS_BACKEND", "console")

    def _send_sms(self, phone: str, message: str) -> bool:
        """Envoie un SMS via le backend configuré."""
        if not self.enabled:
            logger.warning(f"SMS désactivé. Message pour {phone}: {message[:50]}...")
            return False

        # TODO: Implémenter les backends réels (Twilio, Africa's Talking)
        logger.info(f"SMS envoyé à {phone}: {message[:50]}...")
        return True

    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        if verification_type != "phone" or not user.phone:
            return False

        message = f"School System - Votre code: {code}. Valide 10 min."
        return self._send_sms(user.phone, message)

    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        if reset_type != "phone" or not user.phone:
            return False

        message = f"School System - Code de reinitialisation: {code}. Valide 10 min."
        return self._send_sms(user.phone, message)

    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        if not user.phone:
            return False

        message = f"School System - Nouvelle connexion depuis {ip_address}."
        return self._send_sms(user.phone, message)
