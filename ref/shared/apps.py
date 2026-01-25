"""Configuration de l'application shared."""

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SharedConfig(AppConfig):
    """Configuration du module shared."""

    name = "domain.shared"
    verbose_name = _("Composants Partagés")
    default_auto_field = "django.db.models.BigAutoField"
