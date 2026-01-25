# domain/accounts/services/notifications/console.py

"""
Service de notification console pour le développement.
Affiche les messages dans la console/logs au lieu de les envoyer.
"""

import logging
from typing import TYPE_CHECKING

from .base import BaseNotificationService

if TYPE_CHECKING:
    from domain.accounts.models import CustomUser

logger = logging.getLogger(__name__)


class ConsoleNotificationService(BaseNotificationService):
    """
    Service de notification pour le développement.
    Affiche les messages dans la console.
    """

    def _log_notification(self, notification_type: str, recipient: str, message: str):
        """Affiche la notification dans la console."""
        separator = "=" * 60
        print(f"\n{separator}")
        print(f"📧 NOTIFICATION ({notification_type.upper()})")
        print(f"📬 Destinataire: {recipient}")
        print(f"{separator}")
        print(message)
        print(f"{separator}\n")

        logger.info(f"[{notification_type}] → {recipient}: {message[:50]}...")

    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        """Affiche le code de vérification dans la console."""
        recipient = user.email if verification_type == "email" else user.phone

        if not recipient:
            return False

        message = (
            f"Bonjour {user.first_name},\n\n"
            f"🔐 Votre code de vérification: {code}\n\n"
            f"Ce code expire dans 10 minutes."
        )

        self._log_notification(verification_type, recipient, message)
        return True

    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        """Affiche le code de réinitialisation dans la console."""
        recipient = user.email if reset_type == "email" else user.phone

        if not recipient:
            return False

        message = (
            f"Bonjour {user.first_name},\n\n"
            f"🔑 Votre code de réinitialisation: {code}\n\n"
            f"Ce code expire dans 10 minutes."
        )

        self._log_notification(reset_type, recipient, message)
        return True

    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        """Affiche l'alerte de connexion dans la console."""
        recipient = user.email or user.phone

        if not recipient:
            return False

        message = (
            f"Bonjour {user.first_name},\n\n"
            f"⚠️ Nouvelle connexion détectée\n"
            f"IP: {ip_address}\n"
            f"Appareil: {user_agent[:50]}"
        )

        self._log_notification("login_alert", recipient, message)
        return True
