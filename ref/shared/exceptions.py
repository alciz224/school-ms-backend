"""
Exceptions personnalisées du domaine.

Hiérarchie des exceptions:
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
    Exception de base pour toutes les exceptions du domaine.

    Attributes:
        message: Message d'erreur
        code: Code d'erreur unique
        details: Détails supplémentaires
    """

    default_message = _("Une erreur est survenue.")
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
        Convertit l'exception en dictionnaire.

        Returns:
            Dict avec message, code et details
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
    Exception levée lors d'une erreur de validation.

    Utilisée pour les erreurs de validation métier.
    """

    default_message = _("Les données fournies sont invalides.")
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
    Exception levée quand une ressource n'est pas trouvée.
    """

    default_message = _("La ressource demandée n'existe pas.")
    default_code = "not_found"

    def __init__(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[Any] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if resource_type and resource_id and not message:
            message = _(
                f"{resource_type} avec l'identifiant {resource_id} n'existe pas."
            )

        details = kwargs.pop("details", {})
        if resource_type:
            details["resource_type"] = resource_type
        if resource_id:
            details["resource_id"] = resource_id

        super().__init__(message=message, details=details, **kwargs)


class ConflictException(DomainException):
    """
    Exception levée lors d'un conflit (doublon, violation d'unicité).
    """

    default_message = _("Un conflit a été détecté.")
    default_code = "conflict"

    def __init__(
        self,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if field and value and not message:
            message = _(f"La valeur '{value}' existe déjà pour le champ '{field}'.")

        details = kwargs.pop("details", {})
        if field:
            details["field"] = field
        if value:
            details["value"] = value

        super().__init__(message=message, details=details, **kwargs)


class PermissionDeniedException(DomainException):
    """
    Exception levée quand l'utilisateur n'a pas les permissions requises.
    """

    default_message = _("Vous n'avez pas la permission d'effectuer cette action.")
    default_code = "permission_denied"

    def __init__(
        self,
        action: Optional[str] = None,
        resource: Optional[str] = None,
        message: Optional[str] = None,
        **kwargs,
    ):
        if action and resource and not message:
            message = _(f"Vous n'avez pas la permission de {action} {resource}.")

        details = kwargs.pop("details", {})
        if action:
            details["action"] = action
        if resource:
            details["resource"] = resource

        super().__init__(message=message, details=details, **kwargs)


class BusinessRuleException(DomainException):
    """
    Exception levée lors d'une violation de règle métier.
    """

    default_message = _("Une règle métier a été violée.")
    default_code = "business_rule_violation"

    def __init__(
        self, rule: Optional[str] = None, message: Optional[str] = None, **kwargs
    ):
        details = kwargs.pop("details", {})
        if rule:
            details["rule"] = rule

        super().__init__(message=message, details=details, **kwargs)
