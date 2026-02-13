"""
Constants for the account application.
"""

from django.db import models


class VerificationType(models.TextChoices):
    """Verification type."""

    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"
    SECURITY = "security", "Security Questions"


class VerificationMethod(models.TextChoices):
    """Verification method (subset of types)."""

    EMAIL = "email", "Email"
    PHONE = "phone", "Phone"


class VerificationPurpose(models.TextChoices):
    """Verification purpose."""

    ACCOUNT_VERIFICATION = "verify", "Account Verification"
    PASSWORD_RESET = "reset", "Password Reset"
    LOGIN_OTP = "login", "OTP Login"
    PHONE_CHANGE = "phone_change", "Phone Change"
    EMAIL_CHANGE = "email_change", "Email Change"


class PhoneRemovalReason(models.TextChoices):
    """Reason for phone number removal."""

    CHANGED = "changed", "Changed to a new one"
    LOST = "lost", "Lost / No longer accessible"
    REMOVED = "removed", "Voluntarily removed"
    REPLACED = "replaced", "Replaced by user"


class LoginFailureReason(models.TextChoices):
    """Login failure reason."""

    INVALID_CREDENTIALS = "invalid_credentials", "Invalid credentials"
    ACCOUNT_DISABLED = "account_disabled", "Account disabled"
    ACCOUNT_LOCKED = "account_locked", "Account locked"
    NOT_FOUND = "not_found", "Account not found"


class SecurityLevel(models.TextChoices):
    """Account security level."""

    LOW = "low", "Low"
    MEDIUM = "medium", "Medium"
    HIGH = "high", "High"


# Predefined security questions
PREDEFINED_SECURITY_QUESTIONS = [
    # School context
    "What is the name of your primary school?",
    "What is the name of your favorite teacher?",
    "In which city did you take your first exam?",
    # Family context
    "What is your mother's first name?",
    "What is the name of your childhood neighborhood?",
    "What is your paternal grandfather's first name?",
    # Personal context
    "What is your favorite traditional dish?",
    "What is the name of your childhood best friend?",
    "What is the name of the market closest to your home?",
    "What is the name of your neighborhood mosque or church?",
]
