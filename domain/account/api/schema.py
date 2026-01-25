"""
OpenAPI annotations for documentation.
"""

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
from drf_spectacular.types import OpenApiTypes


# Response examples
REGISTER_SUCCESS_EXAMPLE = {
    "success": True,
    "message": "Account created successfully",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "phone": "+224620123456",
            "first_name": "John",
            "last_name": "Doe",
            "full_name": "John Doe",
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        },
        "requires_verification": True,
        "verification_sent_to": "email",
    },
}

LOGIN_SUCCESS_EXAMPLE = {
    "success": True,
    "message": "Login successful",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "full_name": "John Doe",
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        },
        "requires_verification": False,
    },
}

VALIDATION_ERROR_EXAMPLE = {
    "success": False,
    "message": "Validation error",
    "error": {
        "code": "VALIDATION_ERROR",
        "details": {"email": ["This email is already in use"]},
    },
}

AUTH_ERROR_EXAMPLE = {
    "success": False,
    "message": "Invalid email/phone or password",
    "error": {
        "code": "AUTH_INVALID_CREDENTIALS",
        "details": None,
    },
}

VERIFICATION_SUCCESS_EXAMPLE = {
    "success": True,
    "message": "Verification code sent",
    "data": {
        "sent_to": "email",
        "masked": "u***r@example.com",
        "expires_in": 600,
        "can_resend_in": 60,
    },
}

PROFILE_SUCCESS_EXAMPLE = {
    "success": True,
    "data": {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "email": "user@example.com",
        "phone": "+224620123456",
        "first_name": "John",
        "last_name": "Doe",
        "full_name": "John Doe",
        "email_verified": True,
        "phone_verified": False,
        "is_verified": True,
        "security_summary": {
            "score": 65,
            "level": "medium",
            "suggestions": ["Verify your phone number"],
        },
    },
}

SECURITY_QUESTIONS_EXAMPLE = {
    "success": True,
    "data": {
        "questions": [
            {"order": 1, "question": "What is the name of your primary school?"},
            {"order": 2, "question": "What is your mother's first name?"},
        ],
        "count": 2,
        "max_questions": 3,
    },
}


# Schema decorators
def auth_schema(summary: str, description: str = None):
    """Decorator for authentication endpoints."""
    return extend_schema(
        tags=["Auth"],
        summary=summary,
        description=description,
    )


def user_schema(summary: str, description: str = None):
    """Decorator for user endpoints."""
    return extend_schema(
        tags=["Users"],
        summary=summary,
        description=description,
    )


def verification_schema(summary: str, description: str = None):
    """Decorator for verification endpoints."""
    return extend_schema(
        tags=["Verification"],
        summary=summary,
        description=description,
    )


def security_schema(summary: str, description: str = None):
    """Decorator for security endpoints."""
    return extend_schema(
        tags=["Security"],
        summary=summary,
        description=description,
    )
