"""
Base model for geography entities.

Geography entities are reference data that do not have an active/inactive status.
They use soft delete for data integrity.
"""

from django.db import models

from domain.shared.models.managers import BaseManager, DeletedManager
from domain.shared.models.mixins import (
    TimestampMixin,
    AuthorMixin,
    SoftDeleteMixin,
)


class GeographyBaseModel(TimestampMixin, AuthorMixin, SoftDeleteMixin, models.Model):
    """
    Base model for geography entities.

    Includes:
        - Timestamps: created_at, updated_at
        - Traceability: created_by, updated_by, deleted_by
        - Soft delete: is_deleted, deleted_at

    Note: No is_active field as geography entities are reference data
    that should not be activated/deactivated.

    Managers:
        - objects: Default manager (all non-deleted objects)
        - deleted: Deleted objects only
        - all_objects: All objects (including deleted)
    """

    objects = BaseManager()
    deleted = DeletedManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True
