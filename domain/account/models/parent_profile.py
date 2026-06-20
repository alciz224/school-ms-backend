"""ParentProfile model."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.account.constants import Gender
from domain.account.models.user import CustomUser
from domain.shared.models.base import AuditModel


class ParentProfile(AuditModel):
    """
    Profil parent / tuteur.

    Le parent doit avoir un CustomUser pour accéder au portail parent et
    suivre la scolarité de ses enfants.

    Règles métier :
        - user obligatoire et unique (OneToOne)
        - Un parent peut être rattaché à plusieurs élèves via ParentChild
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="parent_profile",
        verbose_name=_("Compte utilisateur"),
        help_text=_("Compte utilisateur lié."),
    )

    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        verbose_name=_("Sexe"),
        help_text=_("Sexe."),
    )
    occupation = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Profession"),
        help_text=_("Profession (commerçant, fonctionnaire, agriculteur...)."),
    )
    photo = models.ImageField(
        upload_to="profiles/parents/",
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )
    address = models.TextField(
        blank=True,
        verbose_name=_("Adresse"),
        help_text=_("Adresse de résidence."),
    )
    locality = models.ForeignKey(
        "geography.Locality",
        on_delete=models.PROTECT,
        related_name="parents_residing_here",
        null=True,
        blank=True,
        verbose_name=_("Localité"),
        help_text=_("Localité de résidence."),
    )

    class Meta:
        db_table = "parent_profile"
        verbose_name = _("Profil parent")
        verbose_name_plural = _("Profils parents")
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}".strip()
