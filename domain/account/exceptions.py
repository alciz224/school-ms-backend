"""
Custom exceptions for the accounts module.
Mapped to error codes defined in API contracts.
"""

from typing import Any


class AccountsException(Exception):
    """Base exception for accounts module."""

    default_message = "An error occurred"
    default_code = "SERVER_ERROR"
    default_status_code = 400

    def __init__(
        self,
        message: str = None,
        code: str = None,
        details: dict = None,
        status_code: int = None,
    ):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details
        self.status_code = status_code or self.default_status_code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to API response format."""
        return {
            "success": False,
            "message": self.message,
            "error": {"code": self.code, "details": self.details},
        }


# =============================================================================
# AUTHENTICATION
# =============================================================================


class InvalidCredentialsError(AccountsException):
    """Invalid credentials."""

    default_message = "Invalid email/phone or password"
    default_code = "AUTH_INVALID_CREDENTIALS"
    default_status_code = 401


class AccountDisabledError(AccountsException):
    """Account disabled."""

    default_message = "This account has been disabled"
    default_code = "AUTH_ACCOUNT_DISABLED"
    default_status_code = 403


class AccountLockedError(AccountsException):
    """Account locked after too many attempts."""

    default_message = "Account temporarily locked"
    default_code = "AUTH_ACCOUNT_LOCKED"
    default_status_code = 423

    def __init__(self, locked_until=None, remaining_minutes: int = None, **kwargs):
        super().__init__(**kwargs)
        self.details = {
            "locked_until": locked_until.isoformat() if locked_until else None,
            "remaining_minutes": remaining_minutes,
        }


class AuthenticationRequiredError(AccountsException):
    """Authentication required."""

    default_message = "Authentication required"
    default_code = "AUTH_REQUIRED"
    default_status_code = 401


# =============================================================================
# REGISTRATION
# =============================================================================


class EmailAlreadyExistsError(AccountsException):
    """Email already in use."""

    default_message = "This email is already in use"
    default_code = "REGISTER_EMAIL_EXISTS"
    default_status_code = 400


class PhoneAlreadyExistsError(AccountsException):
    """Phone already in use."""

    default_message = "This phone number is already in use"
    default_code = "REGISTER_PHONE_EXISTS"
    default_status_code = 400


class InvalidRegistrationDataError(AccountsException):
    """Invalid registration data."""

    default_message = "Invalid registration data"
    default_code = "REGISTER_INVALID_DATA"
    default_status_code = 400


# =============================================================================
# VERIFICATION
# =============================================================================


class VerificationCodeInvalidError(AccountsException):
    """Invalid verification code."""

    default_message = "Invalid verification code"
    default_code = "VERIFY_CODE_INVALID"
    default_status_code = 400

    def __init__(self, attempts_remaining: int = None, **kwargs):
        super().__init__(**kwargs)
        if attempts_remaining is not None:
            self.details = {"attempts_remaining": attempts_remaining}


class VerificationCodeExpiredError(AccountsException):
    """Expired verification code."""

    default_message = "The verification code has expired"
    default_code = "VERIFY_CODE_EXPIRED"
    default_status_code = 400


class VerificationMaxAttemptsError(AccountsException):
    """Too many verification attempts."""

    default_message = "Too many attempts. Please request a new code."
    default_code = "VERIFY_MAX_ATTEMPTS"
    default_status_code = 429


class AlreadyVerifiedError(AccountsException):
    """Contact already verified."""

    default_message = "This contact is already verified"
    default_code = "VERIFY_ALREADY_VERIFIED"
    default_status_code = 400


class NoContactToVerifyError(AccountsException):
    """No contact to verify."""

    default_message = "No contact of this type to verify"
    default_code = "VERIFY_NO_CONTACT"
    default_status_code = 400


class VerificationCooldownError(AccountsException):
    """Cooldown before new send."""

    default_message = "Please wait before requesting a new code"
    default_code = "VERIFY_COOLDOWN"
    default_status_code = 429

    def __init__(self, retry_after: int = None, **kwargs):
        super().__init__(**kwargs)
        if retry_after is not None:
            self.details = {"retry_after": retry_after}


# =============================================================================
# PASSWORD
# =============================================================================


class InvalidCurrentPasswordError(AccountsException):
    """Invalid current password."""

    default_message = "The current password is incorrect"
    default_code = "PASSWORD_INVALID_CURRENT"
    default_status_code = 400


class WeakPasswordError(AccountsException):
    """Password too weak."""

    default_message = "The password does not meet security requirements"
    default_code = "PASSWORD_TOO_WEAK"
    default_status_code = 400

    def __init__(self, issues: list = None, **kwargs):
        super().__init__(**kwargs)
        if issues:
            self.details = {"issues": issues}


class PasswordResetInvalidError(AccountsException):
    """Invalid reset token."""

    default_message = "Invalid reset link"
    default_code = "PASSWORD_RESET_INVALID"
    default_status_code = 400


class PasswordResetExpiredError(AccountsException):
    """Expired reset token."""

    default_message = "The reset link has expired"
    default_code = "PASSWORD_RESET_EXPIRED"
    default_status_code = 400


# =============================================================================
# SECURITY
# =============================================================================


class SecurityQuestionsRequiredError(AccountsException):
    """Security questions required."""

    default_message = "Please configure your security questions"
    default_code = "SECURITY_QUESTIONS_REQUIRED"
    default_status_code = 400


class SecurityAnswersInvalidError(AccountsException):
    """Invalid security question answers."""

    default_message = "The security question answers are incorrect"
    default_code = "SECURITY_ANSWERS_INVALID"
    default_status_code = 400

    def __init__(self, attempts_remaining: int = None, **kwargs):
        super().__init__(**kwargs)
        if attempts_remaining is not None:
            self.details = {"attempts_remaining": attempts_remaining}


class SecurityMaxAttemptsError(AccountsException):
    """Too many security question attempts."""

    default_message = "Too many attempts. Please try again later."
    default_code = "SECURITY_MAX_ATTEMPTS"
    default_status_code = 429


# =============================================================================
# VALIDATION
# =============================================================================


class ValidationError(AccountsException):
    """General validation error."""

    default_message = "Validation error"
    default_code = "VALIDATION_ERROR"
    default_status_code = 400

    def __init__(self, field_errors: dict = None, **kwargs):
        super().__init__(**kwargs)
        if field_errors:
            self.details = field_errors


class InvalidPhoneFormatError(AccountsException):
    """Invalid phone format."""

    default_message = "The phone number format is invalid"
    default_code = "INVALID_PHONE_FORMAT"
    default_status_code = 400


class InvalidEmailFormatError(AccountsException):
    """Invalid email format."""

    default_message = "The email format is invalid"
    default_code = "INVALID_EMAIL_FORMAT"
    default_status_code = 400


# =============================================================================
# GENERAL
# =============================================================================


class NotFoundError(AccountsException):
    """Resource not found."""

    default_message = "Resource not found"
    default_code = "NOT_FOUND"
    default_status_code = 404


class RateLimitExceededError(AccountsException):
    """Rate limit exceeded."""

    default_message = "Too many requests. Please try again later."
    default_code = "RATE_LIMIT_EXCEEDED"
    default_status_code = 429


class ServerError(AccountsException):
    """Server error."""

    default_message = "An internal error occurred"
    default_code = "SERVER_ERROR"
    default_status_code = 500
