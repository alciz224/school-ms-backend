# domain/accounts/services/notifications/email.py

"""
Service de notification par email.
"""

import logging
from typing import TYPE_CHECKING
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .base import BaseNotificationService

if TYPE_CHECKING:
    from domain.accounts.models import CustomUser

logger = logging.getLogger(__name__)


class EmailNotificationService(BaseNotificationService):
    """Service d'envoi d'emails."""

    def __init__(self):
        self.from_email = getattr(settings, "DEFAULT_FROM_EMAIL", "noreply@school.com")

    def send_verification_code(
        self, user: "CustomUser", code: str, verification_type: str
    ) -> bool:
        """Envoie un code de vérification par email."""
        if verification_type != "email" or not user.email:
            return False

        subject = "Votre code de vérification"

        context = {
            "user": user,
            "code": code,
            "expiry_minutes": settings.ACCOUNTS_CONFIG.get(
                "VERIFICATION_CODE_EXPIRY_MINUTES", 10
            ),
        }

        # Corps du message simple (sans template HTML)
        message = (
            f"Bonjour {user.first_name},\n\n"
            f"Votre code de vérification est : {code}\n\n"
            f"Ce code expire dans {context['expiry_minutes']} minutes.\n\n"
            f"Si vous n'avez pas demandé ce code, ignorez cet email.\n\n"
            f"Cordialement,\n"
            f"L'équipe School Management System"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Email de vérification envoyé à {user.email}")
            return True
        except Exception as e:
            logger.error(f"Erreur envoi email à {user.email}: {e}")
            return False

    def send_password_reset_code(
        self, user: "CustomUser", code: str, reset_type: str
    ) -> bool:
        """Envoie un code de réinitialisation par email."""
        if reset_type != "email" or not user.email:
            return False

        subject = "Réinitialisation de votre mot de passe"

        expiry_minutes = settings.ACCOUNTS_CONFIG.get(
            "VERIFICATION_CODE_EXPIRY_MINUTES", 10
        )

        message = (
            f"Bonjour {user.first_name},\n\n"
            f"Vous avez demandé la réinitialisation de votre mot de passe.\n\n"
            f"Votre code de réinitialisation est : {code}\n\n"
            f"Ce code expire dans {expiry_minutes} minutes.\n\n"
            f"Si vous n'avez pas fait cette demande, "
            f"sécurisez immédiatement votre compte.\n\n"
            f"Cordialement,\n"
            f"L'équipe School Management System"
        )

        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[user.email],
                fail_silently=False,
            )
            logger.info(f"Email reset password envoyé à {user.email}")
            return True
        except Exception as e:
            logger.error(f"Erreur envoi email reset à {user.email}: {e}")
            return False

    def send_login_alert(
        self, user: "CustomUser", ip_address: str, user_agent: str
    ) -> bool:
        """Envoie une alerte de connexion suspecte."""
        if not user.email:
            return False

        subject = "Nouvelle connexion à votre compte"

        message = (
            f"Bonjour {user.first_name},\n\n"
            f"Une nouvelle connexion a été détectée sur votre compte.\n\n"
            f"Détails :\n"
            f"- Adresse IP : {ip_address}\n"
            f"- Appareil : {user_agent[:100]}\n\n"
            f"Si ce n'était pas vous, changez immédiatement votre mot de passe.\n\n"
            f"Cordialement,\n"
            f"L'équipe School Management System"
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
            logger.error(f"Erreur envoi alerte login à {user.email}: {e}")
            return False
