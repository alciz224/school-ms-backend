"""
Constants for school operations domain.

This module defines constants for Guinea's educational system.
"""

from django.utils.translation import gettext_lazy as _
from django.db import models


# School Types (based on Guinea's education system)
class SchoolType(models.TextChoices):
    """School type constants for Guinea."""
    PRESCOLAIRE = 'prescolaire', _('Préscolaire')          # Pre-school (ages 3-6)
    PRIMAIRE = 'primaire', _('Primaire')                # Primary (ages 6-12, CP-CM2)
    COLLEGE = 'college', _('Collège')                  # Lower secondary (ages 12-16, 7e-10e)
    LYCEE = 'lycee', _('Lycée')                      # Upper secondary (ages 16-19, 2nde-Terminale)
    TECHNIQUE = 'technique', _('Technique/Professionnel')              # Technical/vocational
    SUPERIEUR = 'superieur', _('Supérieur')              # Higher education
    FORMATION_PROF = 'formation_prof', _('Formation Professionnelle')    # Professional training


# School Status
class SchoolStatus(models.TextChoices):
    """School operational status."""
    DRAFT = 'draft', _('Brouillon')           # School being planned
    ACTIVE = 'active', _('Actif')         # Operational school
    SUSPENDED = 'suspended', _('Suspendu')   # Temporarily closed
    CLOSED = 'closed', _('Fermé')         # Permanently closed


# School Ownership Types (Guinea context)
class SchoolOwnership(models.TextChoices):
    """School ownership types."""
    PUBLIC = 'public', _('Public')         # Government schools
    PRIVATE = 'private', _('Privé')       # Private schools
    COMMUNITY = 'community', _('Communautaire')   # Community-based schools
    RELIGIOUS = 'religious', _('Religieux')   # Religious schools
    NGO = 'ngo', _('ONG')              # NGO-operated schools


# Guinea-specific settings
# SchoolYear Status
class SchoolYearStatus(models.TextChoices):
    """SchoolYear operational status for Guinea's education system."""
    PLANNING = 'planning', _('Planification')     # Planning phase, not yet active
    ACTIVE = 'active', _('Actif')         # Currently operational
    COMPLETED = 'completed', _('Terminé')   # Year finished, final reports done
    ARCHIVED = 'archived', _('Archivé')     # Historical record, read-only


# Guinea Academic Calendar Settings
GUINEA_ACADEMIC_CALENDAR = {
    'default_start_month': 10,  # October
    'default_end_month': 6,     # June
    'enrollment_period_weeks': 4,  # Typical enrollment period duration
    'holiday_periods': [
        {'name': 'Christmas Break', 'typical_start': (12, 20), 'typical_end': (1, 5)},
        {'name': 'Easter Break', 'typical_start': (4, 1), 'typical_end': (4, 15)},
    ]
}


GUINEA_SCHOOL_SETTINGS = {
    'languages': {
        'instruction_languages': ['french', 'pular', 'malinke', 'soussou'],
        'default_language': 'french'
    },
    'academic': {
        'grading_scales': ['20_point', 'letter_grade', 'competency'],
        'default_grading_scale': '20_point'
    },
    'operations': {
        'typical_capacity_ranges': {
            'prescolaire': (30, 150),
            'primaire': (100, 800),
            'college': (200, 1200),
            'lycee': (300, 1500),
            'technique': (150, 800),
        }
    }
}


# Django models TextChoices for new models
from django.db import models


class SchoolYearTeacherStatus(models.TextChoices):
    """Status for teacher assignment to a school year."""
    ACTIVE = "ACTIVE", "Active"
    SUSPENDED = "SUSPENDED", "Suspended"
    LEFT = "LEFT", "Left"


class TimeSlotStatus(models.TextChoices):
    """Status for time slots."""
    ACTIVE = "ACTIVE", "Active"
    INACTIVE = "INACTIVE", "Inactive"
