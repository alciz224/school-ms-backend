"""
Modèles de base partagés.

Ce module exporte les managers, mixins et modèles de base
utilisés par tous les domaines.
"""

from domain.shared.models.managers import (
    BaseManager,
    ActiveManager,
    DeletedManager,
    InactiveManager,
)

from domain.shared.models.mixins import (
    TimestampMixin,
    AuthorMixin,
    SoftDeleteMixin,
    ActivableMixin,
    OrderableMixin,
    NameMixin,
    CodeMixin,
    DescriptionMixin,
    SingletonMixin,
)

from domain.shared.models.base import (
    BaseModel,
    AuditModel,
)


__all__ = [
    # Managers
    "BaseManager",
    "ActiveManager",
    "DeletedManager",
    "InactiveManager",
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
]
