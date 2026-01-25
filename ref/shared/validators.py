"""
Validateurs réutilisables.

Ce module fournit des validateurs pour les champs de modèles Django,
ainsi que des fonctions de validation standalone.
"""

import re
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible


# =============================================================================
# PATTERNS REGEX
# =============================================================================

# Code standard: lettres majuscules et chiffres, 2-20 caractères
PATTERN_CODE = r"^[A-Z0-9]{2,20}$"

# Code court: lettres majuscules uniquement, 2-10 caractères
PATTERN_SHORT_CODE = r"^[A-Z]{2,10}$"

# Abréviation: lettres majuscules uniquement, 1-10 caractères
PATTERN_ABBREVIATION = r"^[A-Z]{1,10}$"

# Couleur hexadécimale
PATTERN_COLOR_HEX = r"^#[0-9A-Fa-f]{6}$"

# Numéro de téléphone international
PATTERN_PHONE = r"^[+]?[0-9\s\-]{8,20}$"

# Slug (URL-friendly)
PATTERN_SLUG = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


# =============================================================================
# FONCTIONS DE VALIDATION
# =============================================================================


def validate_not_empty(value: Any, field_name: str = "champ") -> None:
    """
    Valide qu'une valeur n'est pas vide.

    Args:
        value: Valeur à valider
        field_name: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si la valeur est vide
    """
    if value is None:
        raise ValidationError(
            _("Le %(field)s ne peut pas être vide."),
            params={"field": field_name},
            code="required",
        )

    if isinstance(value, str) and not value.strip():
        raise ValidationError(
            _("Le %(field)s ne peut pas être vide."),
            params={"field": field_name},
            code="blank",
        )


def validate_code_format(value: str, field_name: str = "code") -> None:
    """
    Valide le format d'un code (2-20 caractères alphanumériques majuscules).

    Args:
        value: Code à valider
        field_name: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si le format est invalide
    """
    if not value:
        return

    if not re.match(PATTERN_CODE, value):
        raise ValidationError(
            _("Le %(field)s doit contenir 2-20 caractères alphanumériques majuscules."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_short_code_format(value: str, field_name: str = "code") -> None:
    """
    Valide le format d'un code court (2-10 lettres majuscules).

    Args:
        value: Code à valider
        field_name: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si le format est invalide
    """
    if not value:
        return

    if not re.match(PATTERN_SHORT_CODE, value):
        raise ValidationError(
            _("Le %(field)s doit contenir 2-10 lettres majuscules."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_color_hex(value: str, field_name: str = "couleur") -> None:
    """
    Valide le format d'une couleur hexadécimale (#RRGGBB).

    Args:
        value: Couleur à valider
        field_name: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si le format est invalide
    """
    if not value:
        return

    if not re.match(PATTERN_COLOR_HEX, value):
        raise ValidationError(
            _("La %(field)s doit être au format hexadécimal (#RRGGBB)."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_phone_number(value: str, field_name: str = "numéro de téléphone") -> None:
    """
    Valide le format d'un numéro de téléphone.

    Args:
        value: Numéro à valider
        field_name: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si le format est invalide
    """
    if not value:
        return

    if not re.match(PATTERN_PHONE, value):
        raise ValidationError(
            _("Le %(field)s n'est pas valide."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_positive(value: Any, field_name: str = "valeur") -> None:
    """
    Valide qu'une valeur numérique est positive.

    Args:
        value: Valeur à valider
        field_name: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si la valeur n'est pas positive
    """
    if value is None:
        return

    try:
        if float(value) <= 0:
            raise ValidationError(
                _("Le %(field)s doit être positif."),
                params={"field": field_name},
                code="not_positive",
            )
    except (TypeError, ValueError):
        raise ValidationError(
            _("Le %(field)s doit être un nombre."),
            params={"field": field_name},
            code="invalid_type",
        )


def validate_percentage(value: Any, field_name: str = "pourcentage") -> None:
    """
    Valide qu'une valeur est un pourcentage valide (0-100).

    Args:
        value: Valeur à valider
        field_name: Nom du champ pour le message d'erreur

    Raises:
        ValidationError: Si la valeur n'est pas un pourcentage valide
    """
    if value is None:
        return

    try:
        val = float(value)
        if val < 0 or val > 100:
            raise ValidationError(
                _("Le %(field)s doit être entre 0 et 100."),
                params={"field": field_name},
                code="out_of_range",
            )
    except (TypeError, ValueError):
        raise ValidationError(
            _("Le %(field)s doit être un nombre."),
            params={"field": field_name},
            code="invalid_type",
        )


# =============================================================================
# CLASSES DE VALIDATION (pour les champs de modèles)
# =============================================================================


@deconstructible
class CodeValidator(RegexValidator):
    """
    Validateur pour les codes (2-20 caractères alphanumériques majuscules).

    Usage:
        code = models.CharField(validators=[CodeValidator()])
    """

    regex = PATTERN_CODE
    message = _("Le code doit contenir 2-20 caractères alphanumériques majuscules.")
    code = "invalid_code"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class ShortCodeValidator(RegexValidator):
    """
    Validateur pour les codes courts (2-10 lettres majuscules).

    Usage:
        code = models.CharField(validators=[ShortCodeValidator()])
    """

    regex = PATTERN_SHORT_CODE
    message = _("Le code doit contenir 2-10 lettres majuscules.")
    code = "invalid_short_code"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class ColorHexValidator(RegexValidator):
    """
    Validateur pour les couleurs hexadécimales (#RRGGBB).

    Usage:
        color = models.CharField(validators=[ColorHexValidator()])
    """

    regex = PATTERN_COLOR_HEX
    message = _("La couleur doit être au format hexadécimal (#RRGGBB).")
    code = "invalid_color"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class PhoneValidator(RegexValidator):
    """
    Validateur pour les numéros de téléphone.

    Usage:
        phone = models.CharField(validators=[PhoneValidator()])
    """

    regex = PATTERN_PHONE
    message = _("Le numéro de téléphone n'est pas valide.")
    code = "invalid_phone"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class AbbreviationValidator(RegexValidator):
    """
    Validateur pour les abréviations (1-10 lettres majuscules).

    Usage:
        abbr = models.CharField(validators=[AbbreviationValidator()])
    """

    regex = PATTERN_ABBREVIATION
    message = _("L'abréviation doit contenir 1-10 lettres majuscules.")
    code = "invalid_abbreviation"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class SlugValidator(RegexValidator):
    """
    Validateur pour les slugs (URL-friendly).

    Usage:
        slug = models.CharField(validators=[SlugValidator()])
    """

    regex = PATTERN_SLUG
    message = _(
        "Le slug ne peut contenir que des lettres minuscules, chiffres et tirets."
    )
    code = "invalid_slug"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )
