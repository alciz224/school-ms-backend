"""
Reusable mixins for models.

This module provides mixins that add common functionality
to models: timestamps, authors, soft delete, etc.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class TimestampMixin(models.Model):
    """
    Mixin adding creation and modification timestamps.

    Attributes:
        created_at: Creation date/time (auto)
        updated_at: Last modification date/time (auto)
    """

    created_at = models.DateTimeField(
        _("created at"), auto_now_add=True, db_index=True, editable=False
    )
    updated_at = models.DateTimeField(_("updated at"), auto_now=True, editable=False)

    class Meta:
        abstract = True


class AuthorMixin(models.Model):
    """
    Mixin to track who created/modified a record.

    Attributes:
        created_by: User who created the record
        updated_by: User who last modified the record

    Usage:
        instance.save_by(user=request.user)
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("created by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("updated by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_updated",
        editable=False,
    )

    class Meta:
        abstract = True

    def save_by(self, user=None, **kwargs):
        """
        Save with user traceability.

        Args:
            user: The user performing the action
            **kwargs: Arguments passed to save()
        """
        if user is not None and hasattr(user, "pk") and user.pk:
            if not self.pk:  # New instance
                self.created_by = user
            self.updated_by = user
        self.save(**kwargs)


class SoftDeleteMixin(models.Model):
    """
    Mixin for soft delete functionality.

    Instead of physically deleting records,
    they are marked as deleted.

    Attributes:
        is_deleted: Flag indicating if the object is deleted
        deleted_at: Deletion date/time
        deleted_by: User who deleted the object

    Usage:
        instance.soft_delete(user=request.user)  # Soft delete
        instance.restore()                        # Restore
        instance.hard_delete()                    # Physical delete
    """

    is_deleted = models.BooleanField(
        _("deleted"), default=False, db_index=True, editable=False
    )
    deleted_at = models.DateTimeField(
        _("deleted at"), null=True, blank=True, editable=False
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("deleted by"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_deleted",
        editable=False,
    )

    class Meta:
        abstract = True

    def soft_delete(self, user=None):
        """
        Perform a soft delete.

        Args:
            user: The user performing the deletion
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()

        if user is not None and hasattr(user, "pk") and user.pk:
            self.deleted_by = user

        # Also deactivate if ActivableMixin is present
        if hasattr(self, "is_active"):
            self.is_active = False

        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
                "deleted_by",
                *(["is_active"] if hasattr(self, "is_active") else []),
                "updated_at",
            ]
        )

    def restore(self, user=None):
        """
        Restore a soft-deleted object.

        Args:
            user: The user performing the restoration
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

        # Update updated_by if AuthorMixin is present
        if hasattr(self, "updated_by") and user is not None:
            self.updated_by = user

        self.save(
            update_fields=[
                "is_deleted",
                "deleted_at",
                "deleted_by",
                *(["updated_by"] if hasattr(self, "updated_by") else []),
                "updated_at",
            ]
        )

    def hard_delete(self, *args, **kwargs):
        """Perform a permanent physical delete."""
        return super().delete(*args, **kwargs)

    def delete(self, using=None, keep_parents=False, hard=False, user=None):
        """
        Override delete() to soft delete by default.

        Args:
            hard: If True, permanent deletion. Otherwise, soft delete.
            user: The user performing the deletion
        """
        if hard:
            return self.hard_delete(using=using, keep_parents=keep_parents)
        return self.soft_delete(user=user)


class ActivableMixin(models.Model):
    """
    Mixin for activation/deactivation management.

    Attributes:
        is_active: Flag indicating if the object is active

    Usage:
        instance.activate()
        instance.deactivate()
    """

    is_active = models.BooleanField(_("active"), default=True, db_index=True)

    class Meta:
        abstract = True

    def activate(self, user=None):
        """Activate the object."""
        # Don't activate if deleted
        if hasattr(self, "is_deleted") and self.is_deleted:
            raise ValidationError(
                _("Cannot activate a deleted object. Restore it first.")
            )

        self.is_active = True

        update_fields = ["is_active", "updated_at"]
        if hasattr(self, "updated_by") and user is not None:
            self.updated_by = user
            update_fields.append("updated_by")

        self.save(update_fields=update_fields)

    def deactivate(self, user=None):
        """Deactivate the object."""
        self.is_active = False

        update_fields = ["is_active", "updated_at"]
        if hasattr(self, "updated_by") and user is not None:
            self.updated_by = user
            update_fields.append("updated_by")

        self.save(update_fields=update_fields)

    def toggle_active(self, user=None):
        """Toggle the active state."""
        if self.is_active:
            self.deactivate(user=user)
        else:
            self.activate(user=user)


class OrderableMixin(models.Model):
    """
    Mixin for orderable objects.

    Attributes:
        order_number: Position in the order (1-based)

    Usage:
        # In Meta.ordering:
        ordering = ['order_number']

        # To get the next order:
        next_order = MyModel.get_next_order(category=cat)
    """

    order_number = models.PositiveIntegerField(_("order"), default=1, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order_number"]

    @classmethod
    def get_next_order(cls, **filters) -> int:
        """
        Return the next available order number.

        Args:
            **filters: Filters for scope (e.g., category=cat1)

        Returns:
            int: Next order number
        """
        from django.db.models import Max

        queryset = cls.objects.all()

        # Apply filters
        if filters:
            queryset = queryset.filter(**filters)

        # Exclude deleted if applicable
        if hasattr(cls, "is_deleted"):
            queryset = queryset.filter(is_deleted=False)

        max_order = queryset.aggregate(max_order=Max("order_number"))["max_order"]
        return (max_order or 0) + 1


class NameMixin(models.Model):
    """
    Mixin for objects with a name.

    Attributes:
        name: Object name
    """

    name = models.CharField(_("name"), max_length=100)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class CodeMixin(models.Model):
    """
    Mixin for objects with a unique code.

    Attributes:
        code: Unique object code
    """

    code = models.CharField(_("code"), max_length=20, unique=True, db_index=True)

    class Meta:
        abstract = True


class DescriptionMixin(models.Model):
    """
    Mixin for objects with an optional description.

    Attributes:
        description: Text description
    """

    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        abstract = True


class SingletonMixin(models.Model):
    """
    Mixin for singleton models (only one instance).

    Usage:
        class SiteSettings(SingletonMixin, BaseModel):
            site_name = models.CharField(...)

        # Get the unique instance
        settings = SiteSettings.get_instance()
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Prevent creation of multiple instances."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """
        Get the unique instance, create if necessary.

        Returns:
            Unique model instance
        """
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance
