"""Academic domain app configuration."""
from django.apps import AppConfig


class AcademicConfig(AppConfig):
    """Configuration for the Academic domain."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "domain.academic"
    verbose_name = "Academic Domain"

    def ready(self):
        """Import signals when app is ready."""
        try:
            import domain.academic.signals  # noqa: F401
        except ImportError:
            pass
