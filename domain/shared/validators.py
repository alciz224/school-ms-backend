"""
Reusable validators.

This module provides validators for Django model fields,
as well as standalone validation functions.
"""

import re
from typing import Any, Optional

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils.deconstruct import deconstructible


# =============================================================================
# REGEX PATTERNS
# =============================================================================

# Standard code: uppercase letters and digits, 2-20 characters
PATTERN_CODE = r"^[A-Z0-9]{2,20}$"

# Short code: uppercase letters only, 2-10 characters
PATTERN_SHORT_CODE = r"^[A-Z]{2,10}$"

# Abbreviation: uppercase letters only, 1-10 characters
PATTERN_ABBREVIATION = r"^[A-Z]{1,10}$"

# Hexadecimal color
PATTERN_COLOR_HEX = r"^#[0-9A-Fa-f]{6}$"

# International phone number
PATTERN_PHONE = r"^[+]?[0-9\s\-]{8,20}$"

# Slug (URL-friendly)
PATTERN_SLUG = r"^[a-z0-9]+(?:-[a-z0-9]+)*$"


# =============================================================================
# VALIDATION FUNCTIONS
# =============================================================================


def validate_not_empty(value: Any, field_name: str = "field") -> None:
    """
    Validate that a value is not empty.

    Args:
        value: Value to validate
        field_name: Field name for error message

    Raises:
        ValidationError: If value is empty
    """
    if value is None:
        raise ValidationError(
            _("The %(field)s cannot be empty."),
            params={"field": field_name},
            code="required",
        )

    if isinstance(value, str) and not value.strip():
        raise ValidationError(
            _("The %(field)s cannot be empty."),
            params={"field": field_name},
            code="blank",
        )


def validate_code_format(value: str, field_name: str = "code") -> None:
    """
    Validate code format (2-20 uppercase alphanumeric characters).

    Args:
        value: Code to validate
        field_name: Field name for error message

    Raises:
        ValidationError: If format is invalid
    """
    if not value:
        return

    if not re.match(PATTERN_CODE, value):
        raise ValidationError(
            _("The %(field)s must contain 2-20 uppercase alphanumeric characters."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_short_code_format(value: str, field_name: str = "code") -> None:
    """
    Validate short code format (2-10 uppercase letters).

    Args:
        value: Code to validate
        field_name: Field name for error message

    Raises:
        ValidationError: If format is invalid
    """
    if not value:
        return

    if not re.match(PATTERN_SHORT_CODE, value):
        raise ValidationError(
            _("The %(field)s must contain 2-10 uppercase letters."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_color_hex(value: str, field_name: str = "color") -> None:
    """
    Validate hexadecimal color format (#RRGGBB).

    Args:
        value: Color to validate
        field_name: Field name for error message

    Raises:
        ValidationError: If format is invalid
    """
    if not value:
        return

    if not re.match(PATTERN_COLOR_HEX, value):
        raise ValidationError(
            _("The %(field)s must be in hexadecimal format (#RRGGBB)."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_phone_number_format(value: str, field_name: str = "phone number") -> None:
    """
    Validate phone number format.

    Args:
        value: Number to validate
        field_name: Field name for error message

    Raises:
        ValidationError: If format is invalid
    """
    if not value:
        return

    if not re.match(PATTERN_PHONE, value):
        raise ValidationError(
            _("The %(field)s is not valid."),
            params={"field": field_name},
            code="invalid_format",
        )


def validate_positive(value: Any, field_name: str = "value") -> None:
    """
    Validate that a numeric value is positive.

    Args:
        value: Value to validate
        field_name: Field name for error message

    Raises:
        ValidationError: If value is not positive
    """
    if value is None:
        return

    try:
        if float(value) <= 0:
            raise ValidationError(
                _("The %(field)s must be positive."),
                params={"field": field_name},
                code="not_positive",
            )
    except (TypeError, ValueError):
        raise ValidationError(
            _("The %(field)s must be a number."),
            params={"field": field_name},
            code="invalid_type",
        )


def validate_percentage(value: Any, field_name: str = "percentage") -> None:
    """
    Validate that a value is a valid percentage (0-100).

    Args:
        value: Value to validate
        field_name: Field name for error message

    Raises:
        ValidationError: If value is not a valid percentage
    """
    if value is None:
        return

    try:
        val = float(value)
        if val < 0 or val > 100:
            raise ValidationError(
                _("The %(field)s must be between 0 and 100."),
                params={"field": field_name},
                code="out_of_range",
            )
    except (TypeError, ValueError):
        raise ValidationError(
            _("The %(field)s must be a number."),
            params={"field": field_name},
            code="invalid_type",
        )


# =============================================================================
# VALIDATION CLASSES (for model fields)
# =============================================================================


@deconstructible
class CodeValidator(RegexValidator):
    """
    Validator for codes (2-20 uppercase alphanumeric characters).

    Usage:
        code = models.CharField(validators=[CodeValidator()])
    """

    regex = PATTERN_CODE
    message = _("The code must contain 2-20 uppercase alphanumeric characters.")
    code = "invalid_code"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class ShortCodeValidator(RegexValidator):
    """
    Validator for short codes (2-10 uppercase letters).

    Usage:
        code = models.CharField(validators=[ShortCodeValidator()])
    """

    regex = PATTERN_SHORT_CODE
    message = _("The code must contain 2-10 uppercase letters.")
    code = "invalid_short_code"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class ColorHexValidator(RegexValidator):
    """
    Validator for hexadecimal colors (#RRGGBB).

    Usage:
        color = models.CharField(validators=[ColorHexValidator()])
    """

    regex = PATTERN_COLOR_HEX
    message = _("The color must be in hexadecimal format (#RRGGBB).")
    code = "invalid_color"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class PhoneValidator(RegexValidator):
    """
    Validator for phone numbers.

    Usage:
        phone = models.CharField(validators=[PhoneValidator()])
    """

    regex = PATTERN_PHONE
    message = _("The phone number is not valid.")
    code = "invalid_phone"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class AbbreviationValidator(RegexValidator):
    """
    Validator for abbreviations (1-10 uppercase letters).

    Usage:
        abbr = models.CharField(validators=[AbbreviationValidator()])
    """

    regex = PATTERN_ABBREVIATION
    message = _("The abbreviation must contain 1-10 uppercase letters.")
    code = "invalid_abbreviation"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )


@deconstructible
class SlugValidator(RegexValidator):
    """
    Validator for slugs (URL-friendly).

    Usage:
        slug = models.CharField(validators=[SlugValidator()])
    """

    regex = PATTERN_SLUG
    message = _("The slug can only contain lowercase letters, numbers, and hyphens.")
    code = "invalid_slug"

    def __init__(self, message: Optional[str] = None, code: Optional[str] = None):
        super().__init__(
            regex=self.regex, message=message or self.message, code=code or self.code
        )
