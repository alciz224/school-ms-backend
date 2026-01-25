# domain/accounts/signals.py

"""
Signaux Django pour le module accounts.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import CustomUser, LoginAttempt

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def user_created_handler(sender, instance, created, **kwargs):
    """Appelé après la création d'un utilisateur."""
    if created:
        logger.info(f"Nouvel utilisateur créé: {instance.identifier}")


@receiver(pre_save, sender=CustomUser)
def user_pre_save_handler(sender, instance, **kwargs):
    """Appelé avant la sauvegarde d'un utilisateur."""
    # Normaliser l'email
    if instance.email:
        instance.email = instance.email.lower().strip()


@receiver(post_save, sender=LoginAttempt)
def login_attempt_handler(sender, instance, created, **kwargs):
    """
    Appelé après une tentative de connexion.
    Peut être utilisé pour envoyer des alertes.
    """
    if created and not instance.success:
        # Vérifier si on doit alerter l'utilisateur
        if instance.user:
            failed_count = LoginAttempt.get_recent_failures(
                identifier=instance.identifier, minutes=30
            )

            # Alerter après 3 échecs
            if failed_count == 3:
                logger.warning(
                    f"3 tentatives de connexion échouées pour "
                    f"{instance.identifier} depuis {instance.ip_address}"
                )
                # TODO: Envoyer une notification à l'utilisateur
