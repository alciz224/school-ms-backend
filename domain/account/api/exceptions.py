"""
Custom exception handler for the API.
Formats all error responses according to the contract.
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    Throttled,
)
from django.core.exceptions import ValidationError as DjangoValidationError

from domain.account.exceptions import AccountsException

logger = logging.getLogger(__name__)


def accounts_exception_handler(exc, context):
    """
    Custom exception handler.

    Formats all errors according to API contract:
    {
        "success": false,
        "message": "...",
        "error": {
            "code": "...",
            "details": {...}
        }
    }
    """
    # Call default handler first
    response = exception_handler(exc, context)

    # Handle our custom exceptions
    if isinstance(exc, AccountsException):
        return Response(exc.to_dict(), status=exc.status_code)

    # Handle DRF validation errors
    if isinstance(exc, DRFValidationError):
        return Response(
            {
                "success": False,
                "message": "Validation error",
                "error": {"code": "VALIDATION_ERROR", "details": exc.detail},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle authentication errors
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return Response(
            {
                "success": False,
                "message": (
                    str(exc.detail)
                    if hasattr(exc, "detail")
                    else "Authentication required"
                ),
                "error": {"code": "AUTH_REQUIRED", "details": None},
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Handle permission errors
    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "message": "Access denied",
                "error": {"code": "PERMISSION_DENIED", "details": None},
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Handle throttling
    if isinstance(exc, Throttled):
        return Response(
            {
                "success": False,
                "message": f"Too many requests. Try again in {exc.wait} seconds.",
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "details": {"retry_after": exc.wait},
                },
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Handle Django validation errors
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                "success": False,
                "message": "Validation error",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "details": (
                        exc.message_dict
                        if hasattr(exc, "message_dict")
                        else {"__all__": exc.messages}
                    ),
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # For other errors, use default response if available
    if response is not None:
        custom_response_data = {
            "success": False,
            "message": "An error occurred",
            "error": {"code": "SERVER_ERROR", "details": response.data},
        }
        response.data = custom_response_data
        return response

    # Unhandled error
    logger.exception(f"Unhandled error: {exc}")
    return Response(
        {
            "success": False,
            "message": "An internal error occurred",
            "error": {"code": "SERVER_ERROR", "details": None},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
