"""
Base interface for notification services.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
from django.conf import settings

if TYPE_CHECKING:
    from domain.account.models import CustomUser


class BaseNotificationService(ABC):
    """Abstract interface for notification services."""

    @abstractmethod
    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        """
        Send a verification code.

        Args:
            user: The recipient user
            code: The verification code
            verification_type: 'email' or 'phone'

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        """
        Send a password reset code.

        Args:
            user: The recipient user
            code: The reset code
            reset_type: 'email' or 'phone'

        Returns:
            True if sent successfully
        """
        pass

    @abstractmethod
    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        """
        Send a suspicious login alert.

        Args:
            user: The concerned user
            ip_address: IP address of the connection
            user_agent: Browser user-agent

        Returns:
            True if sent successfully
        """
        pass


def get_notification_service(notification_type: str) -> BaseNotificationService:
    """
    Factory to get the appropriate notification service.

    Args:
        notification_type: 'email', 'sms', or 'console'

    Returns:
        Notification service instance
    """
    from .email import EmailNotificationService
    from .sms import SMSNotificationService
    from .console import ConsoleNotificationService

    services = {
        "email": EmailNotificationService,
        "sms": SMSNotificationService,
        "phone": SMSNotificationService,  # Alias
        "console": ConsoleNotificationService,
    }

    # Default configuration
    accounts_config = getattr(settings, "ACCOUNTS_CONFIG", {})

    # If SMS disabled, use console
    if notification_type in ("sms", "phone") and not accounts_config.get("SMS_ENABLED", False):
        return ConsoleNotificationService()

    service_class = services.get(notification_type, ConsoleNotificationService)
    return service_class()
