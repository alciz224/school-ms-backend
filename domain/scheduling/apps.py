"""App configuration for scheduling domain."""

from django.apps import AppConfig


class SchedulingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'domain.scheduling'
    verbose_name = 'Scheduling'
