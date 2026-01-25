# apps/accounts/apps.py

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AccountsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "domain.accounts"
    verbose_name = _("Gestion des comptes")

    def ready(self):
        # Import des signaux
        try:
            from . import signals  # noqa: F401
        except ImportError:
            pass
