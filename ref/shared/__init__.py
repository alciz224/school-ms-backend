"""
Module SHARED - Composants partagés entre tous les domaines.

Ce module fournit les classes de base, mixins, managers et utilitaires
utilisés par tous les autres domaines de l'application.

Exports principaux:
    - Modèles de base: BaseModel, AuditModel
    - Mixins: TimestampMixin, AuthorMixin, SoftDeleteMixin, etc.
    - Managers: ActiveManager, DeletedManager, etc.
    - Validators: Validateurs réutilisables
    - Utils: Fonctions utilitaires
"""

from domain.shared.models import (
    # Managers
    ActiveManager,
    DeletedManager,
    InactiveManager,
    BaseManager,
    # Mixins
    TimestampMixin,
    AuthorMixin,
    SoftDeleteMixin,
    ActivableMixin,
    OrderableMixin,
    NameMixin,
    CodeMixin,
    DescriptionMixin,
    SingletonMixin,
    # Modèles de base
    BaseModel,
    AuditModel,
)

from domain.shared.validators import (
    validate_not_empty,
    validate_code_format,
    validate_short_code_format,
    validate_color_hex,
    validate_phone_number,
    validate_positive,
    validate_percentage,
    CodeValidator,
    ShortCodeValidator,
    ColorHexValidator,
    PhoneValidator,
)

from domain.shared.exceptions import (
    DomainException,
    ValidationException,
    NotFoundException,
    ConflictException,
    PermissionDeniedException,
    BusinessRuleException,
)

from domain.shared.utils import (
    get_constraint_name,
    truncate_string,
    normalize_string,
    generate_code,
)


__all__ = [
    # Managers
    "ActiveManager",
    "DeletedManager",
    "InactiveManager",
    "BaseManager",
    # Mixins
    "TimestampMixin",
    "AuthorMixin",
    "SoftDeleteMixin",
    "ActivableMixin",
    "OrderableMixin",
    "NameMixin",
    "CodeMixin",
    "DescriptionMixin",
    "SingletonMixin",
    # Modèles de base
    "BaseModel",
    "AuditModel",
    # Validators
    "validate_not_empty",
    "validate_code_format",
    "validate_short_code_format",
    "validate_color_hex",
    "validate_phone_number",
    "validate_positive",
    "validate_percentage",
    "CodeValidator",
    "ShortCodeValidator",
    "ColorHexValidator",
    "PhoneValidator",
    # Exceptions
    "DomainException",
    "ValidationException",
    "NotFoundException",
    "ConflictException",
    "PermissionDeniedException",
    "BusinessRuleException",
    # Utils
    "get_constraint_name",
    "truncate_string",
    "normalize_string",
    "generate_code",
]
