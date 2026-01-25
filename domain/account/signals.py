"""
Django signals for the accounts module.
"""

import logging
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import CustomUser, LoginAttempt

logger = logging.getLogger(__name__)


@receiver(post_save, sender=CustomUser)
def user_created_handler(sender, instance, created, **kwargs):
    """Called after user creation."""
    if created:
        logger.info(f"New user created: {instance.identifier}")


@receiver(pre_save, sender=CustomUser)
def user_pre_save_handler(sender, instance, **kwargs):
    """Called before saving a user."""
    # Normalize email
    if instance.email:
        instance.email = instance.email.lower().strip()


@receiver(post_save, sender=LoginAttempt)
def login_attempt_handler(sender, instance, created, **kwargs):
    """
    Called after a login attempt.
    Can be used to send alerts.
    """
    if created and not instance.success:
        # Check if we should alert the user
        if instance.user:
            failed_count = LoginAttempt.get_recent_failures(
                identifier=instance.identifier, minutes=30
            )

            # Alert after 3 failures
            if failed_count == 3:
                logger.warning(
                    f"3 failed login attempts for "
                    f"{instance.identifier} from {instance.ip_address}"
                )
                # TODO: Send notification to user
