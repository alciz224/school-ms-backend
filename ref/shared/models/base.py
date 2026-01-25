"""
Modèles de base.

Ce module fournit les modèles abstraits de base utilisés
par tous les modèles du projet.
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
    Modèle de base minimal avec timestamps.

    Utiliser pour les modèles simples sans besoin d'audit complet.

    Includes:
        - created_at: Date de création
        - updated_at: Date de modification
    """

    class Meta:
        abstract = True


class AuditModel(
    TimestampMixin, AuthorMixin, SoftDeleteMixin, ActivableMixin, models.Model
):
    """
    Modèle de base avec audit complet.

    C'est le modèle de base recommandé pour la plupart des entités métier.

    Includes:
        - Timestamps: created_at, updated_at
        - Traçabilité: created_by, updated_by, deleted_by
        - Soft delete: is_deleted, deleted_at
        - Activation: is_active

    Managers:
        - objects: Manager par défaut (tous les objets non supprimés)
        - active: Objets actifs et non supprimés
        - deleted: Objets supprimés
        - inactive: Objets inactifs mais non supprimés
        - all_objects: Tous les objets (y compris supprimés)

    Usage:
        class MyModel(AuditModel):
            name = models.CharField(max_length=100)

            class Meta:
                constraints = [
                    # Ajouter vos contraintes spécifiques
                ]

        # Création avec utilisateur
        obj = MyModel(name="Test")
        obj.save_by(user=request.user)

        # Soft delete
        obj.soft_delete(user=request.user)

        # Restauration
        obj.restore()

        # Requêtes
        MyModel.objects.all()       # Non supprimés
        MyModel.active.all()        # Actifs et non supprimés
        MyModel.deleted.all()       # Supprimés uniquement
        MyModel.all_objects.all()   # Tout
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
        Validation de base.

        Vérifie la cohérence is_active/is_deleted.
        """
        super().clean()

        # Un objet ne peut pas être actif et supprimé
        if self.is_active and self.is_deleted:
            raise ValidationError(
                _("Un objet ne peut pas être actif et supprimé en même temps.")
            )

    def save(self, *args, **kwargs):
        """
        Sauvegarde avec validation.

        Assure la cohérence is_active/is_deleted.
        """
        # Si supprimé, forcer is_active=False
        if self.is_deleted:
            self.is_active = False

        super().save(*args, **kwargs)

    def get_audit_info(self) -> dict:
        """
        Retourne les informations d'audit.

        Returns:
            dict: Informations d'audit
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
