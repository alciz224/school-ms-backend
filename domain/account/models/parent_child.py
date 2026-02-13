"""Parent-Child relationship model."""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from domain.account.models import CustomUser
from domain.shared.models.base import AuditModel


class ParentChild(AuditModel):
    """
    Represents a parent-child relationship between users.
    
    This model links parent users to their children (students) to enable
    parent portal access to view their children's enrollments and performance.
    
    Business Rules:
        - A child can have multiple parents (e.g., mother, father, guardian)
        - A parent can have multiple children
        - Unique per (parent, child) combination
        - Parent and child must be different users
        - Child should typically have STUDENT role (validated at service layer)
        - Parent should typically have PARENT role (validated at service layer)
    """

    parent = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="children_relationships",
        help_text="Parent user account",
    )
    child = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="parent_relationships",
        help_text="Child (student) user account",
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=[
            ("FATHER", "Father"),
            ("MOTHER", "Mother"),
            ("GUARDIAN", "Legal Guardian"),
            ("OTHER", "Other"),
        ],
        default="GUARDIAN",
        help_text="Type of relationship",
    )
    is_primary = models.BooleanField(
        default=False,
        help_text="Whether this is the primary contact for the child",
    )
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the relationship",
    )

    class Meta:
        db_table = "parent_child"
        verbose_name = "Parent-Child Relationship"
        verbose_name_plural = "Parent-Child Relationships"
        ordering = ["child", "parent"]
        indexes = [
            models.Index(fields=["parent"], name="parent_child_parent_idx"),
            models.Index(fields=["child"], name="parent_child_child_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "child"],
                condition=models.Q(is_deleted=False),
                name="unique_parent_child_relationship",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.parent.get_full_name()} -> {self.child.get_full_name()} ({self.relationship_type})"

    def clean(self) -> None:
        """Validate the relationship."""
        super().clean()
        
        # Parent and child must be different users
        if self.parent_id and self.child_id and self.parent_id == self.child_id:
            raise ValidationError(
                _("Parent and child must be different users.")
            )

    def save(self, *args, **kwargs) -> None:
        """Save with validation."""
        self.full_clean()
        super().save(*args, **kwargs)
