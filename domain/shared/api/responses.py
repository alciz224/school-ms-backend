"""
Standardized API response helpers.
"""

from typing import Any, Dict, List, Optional
from rest_framework.response import Response
from rest_framework import status


def api_response(
    data: Any = None,
    message: Optional[str] = None,
    success: bool = True,
    status_code: int = status.HTTP_200_OK,
    code: str = "error",
    details: Optional[Dict] = None,
    field_errors: Optional[Dict[str, List[str]]] = None,
    **extra,
) -> Response:
    """Backward-compatible response helper.

    The codebase historically used `api_response(...)`. Newer code should prefer
    `success_response`, `created_response`, `no_content_response`, and `error_response`.

    Args:
        data: Response payload
        message: Human-readable message
        success: Whether the response indicates success
        status_code: HTTP status code
        code: Error code when `success` is False
        details: Additional error details
        field_errors: Field-specific validation errors
        **extra: Extra fields to merge into the response body

    Returns:
        DRF Response
    """

    if success:
        return success_response(data=data, message=message, status_code=status_code, **extra)

    return error_response(
        message=message or "An error occurred.",
        code=code,
        details=details,
        field_errors=field_errors,
        status_code=status_code,
    )


def success_response(
    data: Any = None,
    message: Optional[str] = None,
    status_code: int = status.HTTP_200_OK,
    **extra
) -> Response:
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        **extra: Additional fields to include

    Returns:
        Response object
    """
    response_data = {"success": True}

    if message:
        response_data["message"] = message

    if data is not None:
        response_data["data"] = data

    response_data.update(extra)

    return Response(response_data, status=status_code)


def created_response(
    data: Any = None,
    message: str = "Resource created successfully.",
    **extra
) -> Response:
    """
    Create a standardized 201 Created response.
    """
    return success_response(
        data=data,
        message=message,
        status_code=status.HTTP_201_CREATED,
        **extra
    )


def no_content_response() -> Response:
    """
    Create a 204 No Content response.
    """
    return Response(status=status.HTTP_204_NO_CONTENT)


def error_response(
    message: str,
    code: str = "error",
    details: Optional[Dict] = None,
    field_errors: Optional[Dict[str, List[str]]] = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
) -> Response:
    """
    Create a standardized error response.

    Args:
        message: Error message
        code: Error code
        details: Additional error details
        field_errors: Field-specific errors
        status_code: HTTP status code

    Returns:
        Response object
    """
    error_data = {
        "code": code,
        "message": message,
    }

    if details:
        error_data["details"] = details

    if field_errors:
        error_data["field_errors"] = field_errors

    return Response(
        {"success": False, "error": error_data},
        status=status_code,
    )


def validation_error_response(
    field_errors: Dict[str, List[str]],
    message: str = "The provided data is invalid.",
) -> Response:
    """
    Create a validation error response.
    """
    return error_response(
        message=message,
        code="validation_error",
        field_errors=field_errors,
        status_code=status.HTTP_400_BAD_REQUEST,
    )


def not_found_response(
    message: str = "Resource not found.",
    resource_type: Optional[str] = None,
    resource_id: Optional[Any] = None,
) -> Response:
    """
    Create a 404 Not Found response.
    """
    details = {}
    if resource_type:
        details["resource_type"] = resource_type
    if resource_id:
        details["resource_id"] = str(resource_id)

    return error_response(
        message=message,
        code="not_found",
        details=details if details else None,
        status_code=status.HTTP_404_NOT_FOUND,
    )


def unauthorized_response(
    message: str = "Authentication required.",
) -> Response:
    """
    Create a 401 Unauthorized response.
    """
    return error_response(
        message=message,
        code="unauthorized",
        status_code=status.HTTP_401_UNAUTHORIZED,
    )


def forbidden_response(
    message: str = "You do not have permission to perform this action.",
) -> Response:
    """
    Create a 403 Forbidden response.
    """
    return error_response(
        message=message,
        code="forbidden",
        status_code=status.HTTP_403_FORBIDDEN,
    )


def conflict_response(
    message: str = "A conflict was detected.",
    field: Optional[str] = None,
    value: Optional[Any] = None,
) -> Response:
    """
    Create a 409 Conflict response.
    """
    details = {}
    if field:
        details["field"] = field
    if value:
        details["value"] = str(value)

    return error_response(
        message=message,
        code="conflict",
        details=details if details else None,
        status_code=status.HTTP_409_CONFLICT,
    )


def paginated_response(
    data: List[Any],
    count: int,
    page: int,
    page_size: int,
    next_url: Optional[str] = None,
    previous_url: Optional[str] = None,
) -> Response:
    """
    Create a paginated response.

    Args:
        data: List of items
        count: Total count
        page: Current page number
        page_size: Items per page
        next_url: URL for next page
        previous_url: URL for previous page

    Returns:
        Response object
    """
    total_pages = (count + page_size - 1) // page_size if page_size > 0 else 0

    return Response(
        {
            "success": True,
            "data": data,
            "pagination": {
                "count": count,
                "total_pages": total_pages,
                "current_page": page,
                "page_size": page_size,
                "has_next": page < total_pages,
                "has_previous": page > 1,
                "next": next_url,
                "previous": previous_url,
            },
        }
    )
