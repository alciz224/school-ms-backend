"""Parent-Child relationship model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.account.constants import ParentRelationshipType
from domain.account.models.parent_profile import ParentProfile
from domain.account.models.student_profile import StudentProfile
from domain.shared.models.base import AuditModel


class ParentChild(AuditModel):
    """
    Relation parent-enfant entre un ParentProfile et un StudentProfile.

    Permet au parent d'accéder via le portail parent aux inscriptions et résultats
    de ses enfants.

    Règles métier :
        - Un enfant peut avoir plusieurs parents (père, mère, tuteur)
        - Un parent peut avoir plusieurs enfants
        - Unique par couple (parent, child)
        - Un seul parent peut être is_primary=True par enfant
    """

    parent = models.ForeignKey(
        ParentProfile,
        on_delete=models.CASCADE,
        related_name="children_relationships",
        verbose_name=_("Parent"),
        help_text=_("Profil parent."),
    )
    child = models.ForeignKey(
        StudentProfile,
        on_delete=models.CASCADE,
        related_name="parent_relationships",
        verbose_name=_("Enfant"),
        help_text=_("Profil élève."),
    )
    relationship_type = models.CharField(
        max_length=20,
        choices=ParentRelationshipType.choices,
        default=ParentRelationshipType.GUARDIAN,
        verbose_name=_("Type de relation"),
        help_text=_("Type de relation."),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Contact principal"),
        help_text=_("Contact principal pour cet enfant."),
    )
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Notes"),
        help_text=_("Notes complémentaires sur la relation."),
    )

    class Meta:
        db_table = "parent_child"
        verbose_name = _("Relation parent-enfant")
        verbose_name_plural = _("Relations parent-enfant")
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
            # Un seul contact principal actif par enfant
            models.UniqueConstraint(
                fields=["child"],
                condition=models.Q(is_deleted=False, is_primary=True),
                name="unique_primary_parent_per_child",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.parent.full_name} → {self.child.full_name} ({self.get_relationship_type_display()})"

    def save(self, *args, **kwargs) -> None:
        self.full_clean()
        super().save(*args, **kwargs)
