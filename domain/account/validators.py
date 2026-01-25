"""
Custom validators for User model fields.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings


def validate_phone_number(value: str) -> str:
    """
    Validate and normalize a phone number.

    Uses phonenumbers library if available, otherwise falls back to regex.

    Args:
        value: Phone number to validate

    Returns:
        Normalized phone number in E.164 format (+224620123456)

    Raises:
        ValidationError: If the number is invalid
    """
    if not value:
        return value

    # Clean the number
    cleaned = re.sub(r"[\s\-\.\(\)]", "", value)

    # Default region
    default_region = getattr(settings, "ACCOUNTS_CONFIG", {}).get(
        "DEFAULT_PHONE_REGION", "GN"
    )

    try:
        import phonenumbers
        from phonenumbers import NumberParseException

        try:
            # Parse the number
            parsed = phonenumbers.parse(cleaned, default_region)

            # Verify validity
            if not phonenumbers.is_valid_number(parsed):
                raise ValidationError(
                    _("This phone number is not valid."), code="invalid_phone"
                )

            # Return in E.164 format
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )

        except NumberParseException as e:
            raise ValidationError(
                _("Invalid phone number format: %(error)s"),
                code="invalid_phone_format",
                params={"error": str(e)},
            )

    except ImportError:
        # Fallback to basic regex validation if phonenumbers is not installed
        # Basic pattern: optional + followed by 8-20 digits
        pattern = r"^\+?[0-9]{8,20}$"
        if not re.match(pattern, cleaned):
            raise ValidationError(
                _("This phone number is not valid."), code="invalid_phone"
            )

        # Add + prefix if not present and starts with country code
        if not cleaned.startswith("+"):
            # Assume default country code for Guinea
            if not cleaned.startswith("224"):
                cleaned = "224" + cleaned
            cleaned = "+" + cleaned

        return cleaned


def validate_guinea_phone(value: str) -> str:
    """
    Validate specifically a Guinean phone number.
    Accepts formats: 620123456, +224620123456, 00224620123456
    """
    normalized = validate_phone_number(value)

    if normalized and not normalized.startswith("+224"):
        raise ValidationError(
            _("Only Guinean phone numbers (+224) are accepted."),
            code="non_guinea_phone",
        )

    return normalized


def validate_password_strength(password: str) -> None:
    """
    Validate password strength.

    Rules:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
    """
    if len(password) < 8:
        raise ValidationError(
            _("The password must contain at least 8 characters."),
            code="password_too_short",
        )

    if not re.search(r"[A-Z]", password):
        raise ValidationError(
            _("The password must contain at least one uppercase letter."),
            code="password_no_upper",
        )

    if not re.search(r"[a-z]", password):
        raise ValidationError(
            _("The password must contain at least one lowercase letter."),
            code="password_no_lower",
        )

    if not re.search(r"[0-9]", password):
        raise ValidationError(
            _("The password must contain at least one digit."),
            code="password_no_digit",
        )


def check_password_strength(password: str) -> dict:
    """
    Evaluate password strength without raising an exception.

    Returns:
        dict with 'score' (0-100) and 'issues' (list of problems)
    """
    score = 0
    issues = []

    # Length
    if len(password) >= 8:
        score += 25
    else:
        issues.append("Minimum 8 characters required")

    if len(password) >= 12:
        score += 10

    # Complexity
    if re.search(r"[A-Z]", password):
        score += 20
    else:
        issues.append("Add an uppercase letter")

    if re.search(r"[a-z]", password):
        score += 20
    else:
        issues.append("Add a lowercase letter")

    if re.search(r"[0-9]", password):
        score += 15
    else:
        issues.append("Add a digit")

    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 10

    return {
        "score": min(score, 100),
        "is_strong": score >= 70 and len(issues) == 0,
        "issues": issues,
    }
