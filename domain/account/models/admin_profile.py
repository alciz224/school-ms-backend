"""AdminProfile model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.account.models.user import CustomUser
from domain.shared.models.base import AuditModel


class AdminProfile(AuditModel):
    """
    Profil administrateur (interne — niveau plateforme).

    Distinct de SchoolAdminProfile : cet admin gère la plateforme entière
    (ex : équipe support, gestionnaires de données).

    Règles métier :
        - user obligatoire et unique (OneToOne)
        - position décrit la fonction (Support, Data Manager...)
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="admin_profile",
        verbose_name=_("Compte utilisateur"),
        help_text=_("Compte utilisateur lié."),
    )

    position = models.CharField(
        max_length=100,
        verbose_name=_("Fonction"),
        help_text=_("Fonction au sein de l'équipe (ex : Support, Data Manager)."),
    )
    photo = models.ImageField(
        upload_to="profiles/admins/",
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )

    class Meta:
        db_table = "admin_profile"
        verbose_name = _("Profil administrateur")
        verbose_name_plural = _("Profils administrateurs")
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name} ({self.position})"
