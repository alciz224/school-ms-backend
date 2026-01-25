"""
Custom rate limiting for the accounts API.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Rate limiting for authentication endpoints.
    5 requests per minute for anonymous users.
    """

    scope = "auth"
    rate = "5/minute"


class VerificationRateThrottle(UserRateThrottle):
    """
    Rate limiting for verification code sending.
    3 requests per minute.
    """

    scope = "verification"
    rate = "3/minute"


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Rate limiting for password reset requests.
    3 requests per hour.
    """

    scope = "password_reset"
    rate = "3/hour"


class SecurityQuestionsRateThrottle(AnonRateThrottle):
    """
    Rate limiting for security questions verification.
    5 requests per hour.
    """

    scope = "security_questions"
    rate = "5/hour"


class RegistrationRateThrottle(AnonRateThrottle):
    """
    Rate limiting for registration.
    10 requests per hour.
    """

    scope = "registration"
    rate = "10/hour"
