# domain/accounts/services/notifications/base.py

"""
Interface de base pour les services de notification.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from django.conf import settings

if TYPE_CHECKING:
    from domain.accounts.models import CustomUser


class BaseNotificationService(ABC):
    """Interface abstraite pour les services de notification."""

    @abstractmethod
    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        """
        Envoie un code de vérification.

        Args:
            user: L'utilisateur destinataire
            code: Le code de vérification
            verification_type: 'email' ou 'phone'

        Returns:
            True si envoyé avec succès
        """
        pass

    @abstractmethod
    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        """
        Envoie un code de réinitialisation de mot de passe.

        Args:
            user: L'utilisateur destinataire
            code: Le code de réinitialisation
            reset_type: 'email' ou 'phone'

        Returns:
            True si envoyé avec succès
        """
        pass

    @abstractmethod
    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        """
        Envoie une alerte de connexion suspecte.

        Args:
            user: L'utilisateur concerné
            ip_address: Adresse IP de la connexion
            user_agent: User-Agent du navigateur

        Returns:
            True si envoyé avec succès
        """
        pass


def get_notification_service(notification_type: str) -> BaseNotificationService:
    """
    Factory pour obtenir le service de notification approprié.

    Args:
        notification_type: 'email', 'sms', ou 'console'

    Returns:
        Instance du service de notification
    """
    from .email import EmailNotificationService
    from .sms import SMSNotificationService
    from .console import ConsoleNotificationService

    services = {
        "email": EmailNotificationService,
        "sms": SMSNotificationService,
        "console": ConsoleNotificationService,
    }

    # Configuration par défaut
    accounts_config = getattr(settings, "ACCOUNTS_CONFIG", {})

    if notification_type == "sms" and not accounts_config.get("SMS_ENABLED", False):
        # SMS désactivé, utiliser console
        return ConsoleNotificationService()

    service_class = services.get(notification_type, ConsoleNotificationService)
    return service_class()
