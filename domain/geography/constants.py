"""
Constants for the geography module.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class AdministrativeUnitType(models.TextChoices):
    """Types of administrative units."""
    
    PREFECTURE = 'PREFECTURE', _('Prefecture')
    COMMUNE = 'COMMUNE', _('Commune')
    SUBPREFECTURE = 'SUBPREFECTURE', _('Subprefecture')
