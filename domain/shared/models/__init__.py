"""
Shared base models.

This module exports managers, mixins, and base models
used by all domains.
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
    # Base models
    "BaseModel",
    "AuditModel",
]
