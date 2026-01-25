"""
Custom domain exceptions.

Exception hierarchy:
    DomainException (base)
    ├── ValidationException
    ├── NotFoundException
    ├── ConflictException
    ├── PermissionDeniedException
    └── BusinessRuleException
"""

from typing import Any, Dict, Optional, List
from django.utils.translation import gettext_lazy as _


class DomainException(Exception):
    """
    Base exception for all domain exceptions.

    Attributes:
        message: Error message
        code: Unique error code
        details: Additional details
    """

    default_message = _("An error occurred.")
    default_code = "domain_error"

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or str(self.default_message)
        self.code = code or self.default_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert exception to dictionary.

        Returns:
            Dict with message, code, and details
        """
        return {
            "message": self.message,
            "code": self.code,
            "details": self.details,
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}(code={self.code}, message={self.message})>"


class ValidationException(DomainException):
    """
    Exception raised for validation errors.

    Used for business validation errors.
    """

    default_message = _("The provided data is invalid.")
    default_code = "validation_error"

    def __init__(
        self,
        message: Optional[str] = None,
        code: Optional[str] = None,
        field_errors: Optional[Dict[str, List[str]]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.field_errors = field_errors or {}
        super().__init__(
            message=message,
            code=code,
            details={**(details or {}), "field_errors": self.field_errors},
        )


class NotFoundException(DomainException):
    """
    Exception raised when a resource is not found.
    """

    default_message = _("The requested resource does not exist.")
    default_code = "not_found"

    def __init__(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[Any] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if resource_type and resource_id and not message:
            message = f"{resource_type} with identifier {resource_id} does not exist."

        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(message=message, details=details, **kwargs)


class ConflictException(DomainException):
    """
    Exception raised for conflicts (duplicate, uniqueness violation).
    """

    default_message = _("A conflict was detected.")
    default_code = "conflict"

    def __init__(
        self,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if field and value and not message:
            message = f"The value '{value}' already exists for field '{field}'."

        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value:
            details["value"] = value

        super().__init__(message=message, details=details, **kwargs)


class PermissionDeniedException(DomainException):
    """
    Exception raised when user lacks required permissions.
    """

    default_message = _("You do not have permission to perform this action.")
    default_code = "permission_denied"

    def __init__(
        self,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if action and resource and not message:
            message = f"You do not have permission to {action} {resource}."

        details = kwargs.pop("details", {})
        if action:
            details["action"] = action
        if resource:
            details["resource"] = resource

        super().__init__(message=message, details=details, **kwargs)


class BusinessRuleException(DomainException):
    """
    Exception raised for business rule violations.
    """

    default_message = _("A business rule was violated.")
    default_code = "business_rule_violation"

    def __init__(
        self, rule: Optional[str] = None, message: Optional[str] = None, **kwargs
    ):
        details = kwargs.pop("details", {})
        if rule:
            details["rule"] = rule

        super().__init__(message=message, details=details, **kwargs)
