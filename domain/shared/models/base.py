"""
Base models.

This module provides abstract base models used
by all models in the project.
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

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
)


class BaseModel(TimestampMixin, models.Model):
    """
    Minimal base model with timestamps.

    Use for simple models without full audit needs.

    Includes:
        - created_at: Creation date
        - updated_at: Modification date
    """

    class Meta:
        abstract = True


class AuditModel(
    TimestampMixin, AuthorMixin, SoftDeleteMixin, ActivableMixin, models.Model
):
    """
    Base model with full audit capabilities.

    This is the recommended base model for most business entities.

    Includes:
        - Timestamps: created_at, updated_at
        - Traceability: created_by, updated_by, deleted_by
        - Soft delete: is_deleted, deleted_at
        - Activation: is_active

    Managers:
        - objects: Default manager (all non-deleted objects)
        - active: Active and non-deleted objects
        - deleted: Deleted objects
        - inactive: Inactive but non-deleted objects
        - all_objects: All objects (including deleted)

    Usage:
        class MyModel(AuditModel):
            name = models.CharField(max_length=100)

            class Meta:
                constraints = [
                    # Add your specific constraints
                ]

        # Create with user
        obj = MyModel(name="Test")
        obj.save_by(user=request.user)

        # Soft delete
        obj.soft_delete(user=request.user)

        # Restore
        obj.restore()

        # Queries
        MyModel.objects.all()       # Non-deleted
        MyModel.active.all()        # Active and non-deleted
        MyModel.deleted.all()       # Deleted only
        MyModel.all_objects.all()   # All
    """

    # Managers
    objects = BaseManager()
    active = ActiveManager()
    deleted = DeletedManager()
    inactive = InactiveManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def clean(self):
        """
        Basic validation.

        Checks is_active/is_deleted consistency.
        """
        super().clean()

        # An object cannot be active and deleted
        if self.is_active and self.is_deleted:
            raise ValidationError(
                _("An object cannot be active and deleted at the same time.")
            )

    def save(self, *args, **kwargs):
        """
        Save with validation.

        Ensures is_active/is_deleted consistency.
        """
        # If deleted, force is_active=False
        if self.is_deleted:
            self.is_active = False

        super().save(*args, **kwargs)

    def get_audit_info(self) -> dict:
        """
        Return audit information.

        Returns:
            dict: Audit information
        """
        return {
            "created_at": self.created_at,
            "created_by": str(self.created_by) if self.created_by else None,
            "updated_at": self.updated_at,
            "updated_by": str(self.updated_by) if self.updated_by else None,
            "is_active": self.is_active,
            "is_deleted": self.is_deleted,
            "deleted_at": self.deleted_at,
            "deleted_by": str(self.deleted_by) if self.deleted_by else None,
        }
