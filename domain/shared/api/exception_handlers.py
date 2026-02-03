"""
Custom exception handlers for DRF.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404

from domain.shared.exceptions import (
    DomainException,
    ValidationException,
    NotFoundException,
    ConflictException,
    PermissionDeniedException,
    BusinessRuleException,
)
from domain.account.exceptions import AccountsException


def custom_exception_handler(exc, context):
    """
    Custom exception handler that converts domain exceptions
    to appropriate API responses.
    """
    # First, let DRF handle its own exceptions
    response = exception_handler(exc, context)

    # Handle domain exceptions
    if isinstance(exc, NotFoundException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    if isinstance(exc, ValidationException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "field_errors": exc.field_errors,
                    "details": exc.details,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(exc, ConflictException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=status.HTTP_409_CONFLICT,
        )

    if isinstance(exc, PermissionDeniedException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    if isinstance(exc, BusinessRuleException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    if isinstance(exc, DomainException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle AccountsException and its subclasses
    if isinstance(exc, AccountsException):
        return Response(
            {
                "success": False,
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details,
                }
            },
            status=exc.status_code,
        )

    # Handle Django's ValidationError
    if isinstance(exc, DjangoValidationError):
        if hasattr(exc, "message_dict"):
            field_errors = exc.message_dict
        elif hasattr(exc, "messages"):
            field_errors = {"non_field_errors": exc.messages}
        else:
            field_errors = {"non_field_errors": [str(exc)]}

        return Response(
            {
                "success": False,
                "error": {
                    "code": "validation_error",
                    "message": "The provided data is invalid.",
                    "field_errors": field_errors,
                }
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Handle Django's Http404
    if isinstance(exc, Http404):
        return Response(
            {
                "success": False,
                "error": {
                    "code": "not_found",
                    "message": str(exc) or "Resource not found.",
                }
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # For DRF handled exceptions, wrap them in our format
    if response is not None:
        error_data = {
            "success": False,
            "error": {
                "code": _get_error_code(response.status_code),
                "message": _get_error_message(response.data),
                "details": response.data if isinstance(response.data, dict) else {"detail": response.data},
            }
        }
        response.data = error_data

    return response


def _get_error_code(status_code: int) -> str:
    """Map status code to error code."""
    code_map = {
        400: "bad_request",
        401: "unauthorized",
        403: "forbidden",
        404: "not_found",
        405: "method_not_allowed",
        409: "conflict",
        422: "unprocessable_entity",
        429: "too_many_requests",
        500: "internal_error",
    }
    return code_map.get(status_code, "error")


def _get_error_message(data) -> str:
    """Extract error message from response data."""
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])
        if "message" in data:
            return str(data["message"])
        # For field errors, provide generic message
        return "Request failed. Please check the details."
    if isinstance(data, list) and data:
        return str(data[0])
    return str(data)
