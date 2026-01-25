# domain/accounts/services/notifications/__init__.py

"""
Service de notifications.
"""

from .base import BaseNotificationService, get_notification_service
from .email import EmailNotificationService
from .sms import SMSNotificationService
from .console import ConsoleNotificationService

__all__ = [
    "BaseNotificationService",
    "get_notification_service",
    "EmailNotificationService",
    "SMSNotificationService",
    "ConsoleNotificationService",
]
