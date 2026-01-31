"""
Validators for school operations domain.

Guinea-specific validation logic for schools.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .constants import SchoolType, GUINEA_SCHOOL_SETTINGS


def validate_school_code(value: str) -> None:
    """
    Validate school code format for Guinea.
    
    Expected format: TYPE-LOCALITY-NUM (e.g., LYC-FILIMA-001, PRIM-KASSAPO-002)
    
    Args:
        value: School code to validate
        
    Raises:
        ValidationError: If code format is invalid
    """
    if not value:
        return
    
    # Pattern: 3-4 letter type, locality code, 3-digit number
    pattern = r'^[A-Z]{3,4}-[A-Z0-9]{3,10}-\d{3}$'
    
    if not re.match(pattern, value.upper()):
        raise ValidationError(
            _('Code école invalide. Format attendu: TYPE-LOCALITE-NUM '
              '(ex: LYC-FILIMA-001, PRIM-KASSAPO-002)')
        )


def validate_guinea_phone(value: str) -> None:
    """
    Validate Guinea phone number format.
    
    Guinea phone formats:
    - Mobile: +224 6XX XXX XXX or +224 7XX XXX XXX
    - Fixed: +224 30X XXX XXX
    
    Args:
        value: Phone number to validate
        
    Raises:
        ValidationError: If phone format is invalid
    """
    if not value:
        return
    
    # Remove spaces and common separators
    clean_number = re.sub(r'[\s\-\(\)]', '', value)
    
    # Guinea patterns
    patterns = [
        r'^\+224[67]\d{8}$',    # Mobile: +224 6/7XX XXX XXX
        r'^224[67]\d{8}$',      # Mobile without +
        r'^\+22430\d{7}$',      # Fixed: +224 30X XXX XXX
        r'^22430\d{7}$',        # Fixed without +
        r'^[67]\d{8}$',         # Local mobile format
        r'^30\d{7}$',           # Local fixed format
    ]
    
    if not any(re.match(pattern, clean_number) for pattern in patterns):
        raise ValidationError(
            _('Numéro de téléphone Guinée invalide. '
              'Formats acceptés: +224 6XX XXX XXX, +224 7XX XXX XXX, +224 30X XXX XXX')
        )


def validate_school_capacity(value: int, school_type: str) -> None:
    """
    Validate school capacity based on type and Guinea standards.
    
    Args:
        value: Capacity to validate
        school_type: Type of school
        
    Raises:
        ValidationError: If capacity is unrealistic for the school type
    """
    if not value or value <= 0:
        return
    
    # Get typical ranges for Guinea schools
    ranges = GUINEA_SCHOOL_SETTINGS['operations']['typical_capacity_ranges']
    
    if school_type in ranges:
        min_cap, max_cap = ranges[school_type]
        if value < min_cap or value > max_cap:
            raise ValidationError(
                _('Capacité inhabituelle pour ce type d\'école. '
                  f'Gamme typique: {min_cap}-{max_cap} élèves.')
            )


def validate_school_settings(value: dict) -> None:
    """
    Validate school settings JSON structure.
    
    Args:
        value: Settings dictionary to validate
        
    Raises:
        ValidationError: If settings structure is invalid
    """
    if not isinstance(value, dict):
        raise ValidationError(_('Les paramètres doivent être un objet JSON valide.'))
    
    # Validate known setting categories
    allowed_categories = ['academic', 'operations', 'contact', 'languages', 'policies']
    
    for category in value.keys():
        if category not in allowed_categories:
            raise ValidationError(
                _(f'Catégorie de paramètres non reconnue: {category}. '
                  f'Autorisées: {", ".join(allowed_categories)}')
            )
    
    # Validate academic settings if present
    if 'academic' in value:
        academic = value['academic']
        if not isinstance(academic, dict):
            raise ValidationError(_('Les paramètres académiques doivent être un objet.'))
        
        # Validate grading scale
        if 'grading_scale' in academic:
            valid_scales = GUINEA_SCHOOL_SETTINGS['academic']['grading_scales']
            if academic['grading_scale'] not in valid_scales:
                raise ValidationError(
                    _(f'Échelle de notation invalide. Autorisées: {", ".join(valid_scales)}')
                )
    
    # Validate languages if present
    if 'languages' in value:
        languages = value['languages']
        if not isinstance(languages, dict):
            raise ValidationError(_('Les paramètres de langues doivent être un objet.'))
        
        if 'instruction_languages' in languages:
            valid_languages = GUINEA_SCHOOL_SETTINGS['languages']['instruction_languages']
            for lang in languages['instruction_languages']:
                if lang not in valid_languages:
                    raise ValidationError(
                        _(f'Langue d\'instruction non reconnue: {lang}. '
                          f'Autorisées: {", ".join(valid_languages)}')
                    )


def validate_school_year_dates(start_date, end_date) -> None:
    """
    Validate school year date range.
    
    Args:
        start_date: Start date of school year
        end_date: End date of school year
        
    Raises:
        ValidationError: If dates are invalid
    """
    if start_date and end_date:
        if end_date <= start_date:
            raise ValidationError(
                _('La date de fin doit être postérieure à la date de début.')
            )
        
        # School year should be reasonable duration (6-12 months)
        duration = (end_date - start_date).days
        if duration < 180:  # Less than 6 months
            raise ValidationError(
                _('Une année scolaire doit durer au moins 6 mois.')
            )
        if duration > 400:  # More than ~13 months
            raise ValidationError(
                _('Une année scolaire ne peut pas dépasser 13 mois.')
            )


def validate_enrollment_period(enrollment_start, enrollment_end, year_start_date) -> None:
    """
    Validate enrollment period dates.
    
    Args:
        enrollment_start: Enrollment period start
        enrollment_end: Enrollment period end
        year_start_date: School year start date
        
    Raises:
        ValidationError: If enrollment dates are invalid
    """
    if enrollment_start and enrollment_end:
        if enrollment_end <= enrollment_start:
            raise ValidationError(
                _('La fin des inscriptions doit être postérieure au début.')
            )
        
        # Enrollment period should be reasonable (1-12 weeks)
        duration = (enrollment_end - enrollment_start).days
        if duration < 7:  # Less than 1 week
            raise ValidationError(
                _('La période d\'inscription doit durer au moins 1 semaine.')
            )
        if duration > 90:  # More than ~13 weeks
            raise ValidationError(
                _('La période d\'inscription ne peut pas dépasser 12 semaines.')
            )
    
    # Enrollment should end before or at year start
    if enrollment_end and year_start_date:
        if enrollment_end > year_start_date:
            raise ValidationError(
                _('La période d\'inscription doit se terminer avant ou '
                  'au début de l\'année scolaire.')
            )


def validate_school_year_capacity(capacity: int, school) -> None:
    """
    Validate school year capacity against school's total capacity.
    
    Args:
        capacity: School year capacity
        school: School instance
        
    Raises:
        ValidationError: If capacity exceeds school capacity
    """
    if capacity and school and school.capacity:
        if capacity > school.capacity:
            raise ValidationError(
                _(f'La capacité de l\'année scolaire ({capacity}) ne peut pas '
                  f'dépasser la capacité de l\'école ({school.capacity}).')
            )
        
        if capacity <= 0:
            raise ValidationError(
                _('La capacité doit être supérieure à 0.')
            )


def validate_school_year_settings(value: dict) -> None:
    """
    Validate school year settings JSON structure.
    
    Args:
        value: Settings dictionary to validate
        
    Raises:
        ValidationError: If settings structure is invalid
    """
    if not isinstance(value, dict):
        raise ValidationError(_('Les paramètres doivent être un objet JSON valide.'))
    
    # Validate known setting categories for school year
    allowed_categories = [
        'grading_periods', 'holidays', 'attendance', 'assessment', 
        'calendar', 'policies', 'notifications'
    ]
    
    for category in value.keys():
        if category not in allowed_categories:
            raise ValidationError(
                _(f'Catégorie de paramètres non reconnue: {category}. '
                  f'Autorisées: {", ".join(allowed_categories)}')
            )
    
    # Validate grading periods if present
    if 'grading_periods' in value:
        grading = value['grading_periods']
        if not isinstance(grading, dict):
            raise ValidationError(_('Les paramètres des périodes de notation doivent être un objet.'))
    
    # Validate holidays if present
    if 'holidays' in value:
        holidays = value['holidays']
        if not isinstance(holidays, list):
            raise ValidationError(_('Les jours fériés doivent être une liste.'))
        
        for holiday in holidays:
            if not isinstance(holiday, dict):
                raise ValidationError(_('Chaque jour férié doit être un objet.'))
            if 'name' not in holiday or 'start_date' not in holiday:
                raise ValidationError(
                    _('Chaque jour férié doit avoir un nom et une date de début.')
                )