"""
Mixins réutilisables pour les modèles.

Ce module fournit des mixins qui ajoutent des fonctionnalités
communes aux modèles : timestamps, auteurs, soft delete, etc.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError


class TimestampMixin(models.Model):
    """
    Mixin ajoutant les timestamps de création et modification.

    Attributes:
        created_at: Date/heure de création (auto)
        updated_at: Date/heure de dernière modification (auto)
    """

    created_at = models.DateTimeField(
        _("créé le"), auto_now_add=True, db_index=True, editable=False
    )
    updated_at = models.DateTimeField(_("modifié le"), auto_now=True, editable=False)

    class Meta:
        abstract = True


class AuthorMixin(models.Model):
    """
    Mixin pour tracer qui a créé/modifié un enregistrement.

    Attributes:
        created_by: Utilisateur qui a créé l'enregistrement
        updated_by: Utilisateur qui a fait la dernière modification

    Usage:
        instance.save_by(user=request.user)
    """

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("créé par"),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(app_label)s_%(class)s_created",
        editable=False,
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("modifié par"),
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
        Sauvegarde avec traçabilité utilisateur.

        Args:
            user: L'utilisateur effectuant l'action
            **kwargs: Arguments passés à save()
        """
        if user is not None and hasattr(user, "pk") and user.pk:
            if not self.pk:  # Nouvelle instance
                self.created_by = user
            self.updated_by = user
        self.save(**kwargs)


class SoftDeleteMixin(models.Model):
    """
    Mixin pour la suppression logique (soft delete).

    Au lieu de supprimer physiquement les enregistrements,
    on les marque comme supprimés.

    Attributes:
        is_deleted: Flag indiquant si l'objet est supprimé
        deleted_at: Date/heure de suppression
        deleted_by: Utilisateur qui a supprimé

    Usage:
        instance.soft_delete(user=request.user)  # Suppression logique
        instance.restore()                        # Restauration
        instance.hard_delete()                    # Suppression physique
    """

    is_deleted = models.BooleanField(
        _("supprimé"), default=False, db_index=True, editable=False
    )
    deleted_at = models.DateTimeField(
        _("supprimé le"), null=True, blank=True, editable=False
    )
    deleted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_("supprimé par"),
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
        Effectue une suppression logique.

        Args:
            user: L'utilisateur effectuant la suppression
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()

        if user is not None and hasattr(user, "pk") and user.pk:
            self.deleted_by = user

        # Désactiver également si le mixin ActivableMixin est présent
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
        Restaure un objet supprimé logiquement.

        Args:
            user: L'utilisateur effectuant la restauration
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None

        # Mettre à jour updated_by si AuthorMixin est présent
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
        """Effectue une suppression physique définitive."""
        return super().delete(*args, **kwargs)

    def delete(self, using=None, keep_parents=False, hard=False, user=None):
        """
        Override de delete() pour soft delete par défaut.

        Args:
            hard: Si True, suppression définitive. Sinon, soft delete.
            user: L'utilisateur effectuant la suppression
        """
        if hard:
            return self.hard_delete(using=using, keep_parents=keep_parents)
        return self.soft_delete(user=user)


class ActivableMixin(models.Model):
    """
    Mixin pour gérer l'activation/désactivation.

    Attributes:
        is_active: Flag indiquant si l'objet est actif

    Usage:
        instance.activate()
        instance.deactivate()
    """

    is_active = models.BooleanField(_("actif"), default=True, db_index=True)

    class Meta:
        abstract = True

    def activate(self, user=None):
        """Active l'objet."""
        # Ne pas activer si supprimé
        if hasattr(self, "is_deleted") and self.is_deleted:
            raise ValidationError(
                _("Impossible d'activer un objet supprimé. Restaurez-le d'abord.")
            )

        self.is_active = True

        update_fields = ["is_active", "updated_at"]
        if hasattr(self, "updated_by") and user is not None:
            self.updated_by = user
            update_fields.append("updated_by")

        self.save(update_fields=update_fields)

    def deactivate(self, user=None):
        """Désactive l'objet."""
        self.is_active = False

        update_fields = ["is_active", "updated_at"]
        if hasattr(self, "updated_by") and user is not None:
            self.updated_by = user
            update_fields.append("updated_by")

        self.save(update_fields=update_fields)

    def toggle_active(self, user=None):
        """Inverse l'état actif."""
        if self.is_active:
            self.deactivate(user=user)
        else:
            self.activate(user=user)


class OrderableMixin(models.Model):
    """
    Mixin pour les objets ordonnables.

    Attributes:
        order_number: Position dans l'ordre (1-based)

    Usage:
        # Dans Meta.ordering:
        ordering = ['order_number']

        # Pour obtenir le prochain ordre:
        next_order = MyModel.get_next_order(category=cat)
    """

    order_number = models.PositiveIntegerField(_("ordre"), default=1, db_index=True)

    class Meta:
        abstract = True
        ordering = ["order_number"]

    @classmethod
    def get_next_order(cls, **filters) -> int:
        """
        Retourne le prochain numéro d'ordre disponible.

        Args:
            **filters: Filtres pour le scope (ex: category=cat1)

        Returns:
            int: Prochain numéro d'ordre
        """
        from django.db.models import Max

        queryset = cls.objects.all()

        # Appliquer les filtres
        if filters:
            queryset = queryset.filter(**filters)

        # Exclure les supprimés si applicable
        if hasattr(cls, "is_deleted"):
            queryset = queryset.filter(is_deleted=False)

        max_order = queryset.aggregate(max_order=Max("order_number"))["max_order"]
        return (max_order or 0) + 1


class NameMixin(models.Model):
    """
    Mixin pour les objets avec nom.

    Attributes:
        name: Nom de l'objet
    """

    name = models.CharField(_("nom"), max_length=100)

    class Meta:
        abstract = True

    def __str__(self) -> str:
        return self.name


class CodeMixin(models.Model):
    """
    Mixin pour les objets avec code unique.

    Attributes:
        code: Code unique de l'objet
    """

    code = models.CharField(_("code"), max_length=20, unique=True, db_index=True)

    class Meta:
        abstract = True


class DescriptionMixin(models.Model):
    """
    Mixin pour les objets avec description optionnelle.

    Attributes:
        description: Description textuelle
    """

    description = models.TextField(_("description"), blank=True, null=True)

    class Meta:
        abstract = True


class SingletonMixin(models.Model):
    """
    Mixin pour les modèles singleton (une seule instance).

    Usage:
        class SiteSettings(SingletonMixin, BaseModel):
            site_name = models.CharField(...)

        # Récupérer l'instance unique
        settings = SiteSettings.get_instance()
    """

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """Empêche la création de plusieurs instances."""
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        """
        Récupère l'instance unique, la crée si nécessaire.

        Returns:
            Instance unique du modèle
        """
        instance, _ = cls.objects.get_or_create(pk=1)
        return instance
