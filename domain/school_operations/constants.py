"""
Constants for school operations domain.

This module defines constants for Guinea's educational system.
"""

from django.utils.translation import gettext_lazy as _


# School Types (based on Guinea's education system)
class SchoolType:
    """School type constants for Guinea."""
    PRESCOLAIRE = 'prescolaire'          # Pre-school (ages 3-6)
    PRIMAIRE = 'primaire'                # Primary (ages 6-12, CP-CM2)
    COLLEGE = 'college'                  # Lower secondary (ages 12-16, 7e-10e)
    LYCEE = 'lycee'                      # Upper secondary (ages 16-19, 2nde-Terminale)
    TECHNIQUE = 'technique'              # Technical/vocational
    SUPERIEUR = 'superieur'              # Higher education
    FORMATION_PROF = 'formation_prof'    # Professional training

    CHOICES = [
        (PRESCOLAIRE, _('Préscolaire')),
        (PRIMAIRE, _('Primaire')),
        (COLLEGE, _('Collège')),
        (LYCEE, _('Lycée')),
        (TECHNIQUE, _('Technique/Professionnel')),
        (SUPERIEUR, _('Supérieur')),
        (FORMATION_PROF, _('Formation Professionnelle')),
    ]


# School Status
class SchoolStatus:
    """School operational status."""
    DRAFT = 'draft'           # School being planned
    ACTIVE = 'active'         # Operational school
    SUSPENDED = 'suspended'   # Temporarily closed
    CLOSED = 'closed'         # Permanently closed

    CHOICES = [
        (DRAFT, _('Brouillon')),
        (ACTIVE, _('Actif')),
        (SUSPENDED, _('Suspendu')),
        (CLOSED, _('Fermé')),
    ]


# School Ownership Types (Guinea context)
class SchoolOwnership:
    """School ownership types."""
    PUBLIC = 'public'         # Government schools
    PRIVATE = 'private'       # Private schools
    COMMUNITY = 'community'   # Community-based schools
    RELIGIOUS = 'religious'   # Religious schools
    NGO = 'ngo'              # NGO-operated schools

    CHOICES = [
        (PUBLIC, _('Public')),
        (PRIVATE, _('Privé')),
        (COMMUNITY, _('Communautaire')),
        (RELIGIOUS, _('Religieux')),
        (NGO, _('ONG')),
    ]


# Guinea-specific settings
# SchoolYear Status
class SchoolYearStatus:
    """SchoolYear operational status for Guinea's education system."""
    PLANNING = 'planning'     # Planning phase, not yet active
    ACTIVE = 'active'         # Currently operational
    COMPLETED = 'completed'   # Year finished, final reports done
    ARCHIVED = 'archived'     # Historical record, read-only

    CHOICES = [
        (PLANNING, _('Planification')),
        (ACTIVE, _('Actif')),
        (COMPLETED, _('Terminé')),
        (ARCHIVED, _('Archivé')),
    ]


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