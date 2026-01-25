"""
Managers personnalisés.

Ce module fournit des managers réutilisables pour les modèles.
"""

from django.db import models
from django.db.models import QuerySet


class BaseQuerySet(QuerySet):
    """
    QuerySet de base avec méthodes communes.
    """

    def active(self):
        """Filtre les objets actifs."""
        return self.filter(is_active=True)

    def inactive(self):
        """Filtre les objets inactifs."""
        return self.filter(is_active=False)

    def not_deleted(self):
        """Filtre les objets non supprimés."""
        return self.filter(is_deleted=False)

    def deleted(self):
        """Filtre les objets supprimés."""
        return self.filter(is_deleted=True)

    def active_and_not_deleted(self):
        """Filtre les objets actifs et non supprimés."""
        return self.filter(is_active=True, is_deleted=False)


class BaseManager(models.Manager):
    """
    Manager de base utilisant BaseQuerySet.

    Fournit un accès au QuerySet personnalisé et expose
    les méthodes de filtrage au niveau du manager.
    """

    def get_queryset(self) -> BaseQuerySet:
        """Retourne le QuerySet personnalisé."""
        return BaseQuerySet(self.model, using=self._db)

    def active(self):
        """Retourne les objets actifs."""
        return self.get_queryset().active()

    def inactive(self):
        """Retourne les objets inactifs."""
        return self.get_queryset().inactive()

    def not_deleted(self):
        """Retourne les objets non supprimés."""
        return self.get_queryset().not_deleted()

    def deleted(self):
        """Retourne les objets supprimés."""
        return self.get_queryset().deleted()

    def active_and_not_deleted(self):
        """Retourne les objets actifs et non supprimés."""
        return self.get_queryset().active_and_not_deleted()


class ActiveManager(models.Manager):
    """
    Manager qui retourne uniquement les objets actifs et non supprimés.

    Usage:
        class MyModel(AuditModel):
            objects = models.Manager()  # Manager par défaut
            active = ActiveManager()    # Seulement actifs

        # Utilisation
        MyModel.active.all()  # Équivalent à .filter(is_active=True, is_deleted=False)
    """

    def get_queryset(self) -> QuerySet:
        """Retourne uniquement les objets actifs et non supprimés."""
        return super().get_queryset().filter(is_active=True, is_deleted=False)


class DeletedManager(models.Manager):
    """
    Manager qui retourne uniquement les objets supprimés (soft delete).

    Usage:
        class MyModel(AuditModel):
            deleted = DeletedManager()

        # Utilisation
        MyModel.deleted.all()  # Équivalent à .filter(is_deleted=True)
    """

    def get_queryset(self) -> QuerySet:
        """Retourne uniquement les objets supprimés."""
        return super().get_queryset().filter(is_deleted=True)


class InactiveManager(models.Manager):
    """
    Manager qui retourne uniquement les objets inactifs (non supprimés).

    Usage:
        class MyModel(AuditModel):
            inactive = InactiveManager()

        # Utilisation
        MyModel.inactive.all()  # Équivalent à .filter(is_active=False, is_deleted=False)
    """

    def get_queryset(self) -> QuerySet:
        """Retourne uniquement les objets inactifs non supprimés."""
        return super().get_queryset().filter(is_active=False, is_deleted=False)
