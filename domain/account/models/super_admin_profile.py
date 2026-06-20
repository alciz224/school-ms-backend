"""SuperAdminProfile model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.account.models.user import CustomUser
from domain.shared.models.base import AuditModel


class SuperAdminProfile(AuditModel):
    """
    Profil super-administrateur (gouvernance plateforme).

    Niveau le plus élevé : gestion des écoles, des admins école, des paramètres globaux.

    Règles métier :
        - user obligatoire et unique (OneToOne)
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="super_admin_profile",
        verbose_name=_("Compte utilisateur"),
        help_text=_("Compte utilisateur lié."),
    )

    department = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Service / Département"),
        help_text=_("Service / département (ex : DGESS, Inspection régionale)."),
    )
    photo = models.ImageField(
        upload_to="profiles/super_admins/",
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )

    class Meta:
        db_table = "super_admin_profile"
        verbose_name = _("Profil super-administrateur")
        verbose_name_plural = _("Profils super-administrateurs")
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}".strip()
