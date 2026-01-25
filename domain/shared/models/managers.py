"""
Custom managers for models.

This module provides reusable managers for models with soft delete,
activation, and other common filtering needs.
"""

from django.db import models
from django.db.models import QuerySet


class BaseQuerySet(QuerySet):
    """
    Base QuerySet with common filtering methods.
    """

    def active(self):
        """Filter active objects."""
        return self.filter(is_active=True)

    def inactive(self):
        """Filter inactive objects."""
        return self.filter(is_active=False)

    def not_deleted(self):
        """Filter non-deleted objects."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Filter deleted objects."""
        return self.filter(is_deleted=True)

    def active_and_not_deleted(self):
        """Filter active and non-deleted objects."""
        return self.filter(is_active=True, is_deleted=False)


class BaseManager(models.Manager):
    """
    Base manager using BaseQuerySet.

    Provides access to custom QuerySet and exposes
    filtering methods at the manager level.
    """

    def get_queryset(self) -> BaseQuerySet:
        """Return the custom QuerySet."""
        return BaseQuerySet(self.model, using=self._db)

    def active(self):
        """Return active objects."""
        return self.get_queryset().active()

    def inactive(self):
        """Return inactive objects."""
        return self.get_queryset().inactive()

    def not_deleted(self):
        """Return non-deleted objects."""
        return self.get_queryset().not_deleted()

    def deleted(self):
        """Return deleted objects."""
        return self.get_queryset().deleted()

    def active_and_not_deleted(self):
        """Return active and non-deleted objects."""
        return self.get_queryset().active_and_not_deleted()


class ActiveManager(models.Manager):
    """
    Manager that returns only active and non-deleted objects.

    Usage:
        class MyModel(AuditModel):
            objects = models.Manager()  # Default manager
            active = ActiveManager()    # Only active

        # Usage
        MyModel.active.all()  # Equivalent to .filter(is_active=True, is_deleted=False)
    """

    def get_queryset(self) -> QuerySet:
        """Return only active and non-deleted objects."""
        return super().get_queryset().filter(is_active=True, is_deleted=False)


class DeletedManager(models.Manager):
    """
    Manager that returns only soft-deleted objects.

    Usage:
        class MyModel(AuditModel):
            deleted = DeletedManager()

        # Usage
        MyModel.deleted.all()  # Equivalent to .filter(is_deleted=True)
    """

    def get_queryset(self) -> QuerySet:
        """Return only deleted objects."""
        return super().get_queryset().filter(is_deleted=True)


class InactiveManager(models.Manager):
    """
    Manager that returns only inactive (non-deleted) objects.

    Usage:
        class MyModel(AuditModel):
            inactive = InactiveManager()

        # Usage
        MyModel.inactive.all()  # Equivalent to .filter(is_active=False, is_deleted=False)
    """

    def get_queryset(self) -> QuerySet:
        """Return only inactive non-deleted objects."""
        return super().get_queryset().filter(is_active=False, is_deleted=False)
