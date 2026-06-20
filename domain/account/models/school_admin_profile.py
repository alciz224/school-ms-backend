"""SchoolAdminProfile and SchoolAdminAssignment models."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.account.constants import SchoolAdminPosition
from domain.account.models.user import CustomUser
from domain.shared.models.base import AuditModel


class SchoolAdminProfile(AuditModel):
    """
    Profil administrateur d'école.

    Un school admin peut être rattaché à **plusieurs écoles** via SchoolAdminAssignment
    (ex : un directeur supervisant un groupe scolaire avec primaire + collège).

    Règles métier :
        - user obligatoire et unique (OneToOne)
        - Les rattachements aux écoles sont gérés via SchoolAdminAssignment
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="school_admin_profile",
        verbose_name=_("Compte utilisateur"),
        help_text=_("Compte utilisateur lié."),
    )

    photo = models.ImageField(
        upload_to="profiles/school_admins/",
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )

    class Meta:
        db_table = "school_admin_profile"
        verbose_name = _("Profil admin école")
        verbose_name_plural = _("Profils admin école")
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}".strip()

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}".strip()

    @property
    def primary_school(self):
        """Retourne l'école principale (si définie) parmi les affectations actives."""
        return self.assignments.filter(
            is_deleted=False,
            end_date__isnull=True,
            is_primary=True,
        ).select_related("school").first()


class SchoolAdminAssignment(AuditModel):
    """
    Affectation d'un school admin à une école pour une période donnée.

    Permet à un même school admin d'être rattaché à plusieurs écoles
    (ex : directeur d'un groupe scolaire), avec historique complet.

    Règles métier :
        - Une seule affectation active (end_date NULL) par (school_admin, school)
        - start_date < end_date quand end_date renseignée
        - Au plus une affectation is_primary=True par school_admin parmi les actives
    """

    school_admin = models.ForeignKey(
        SchoolAdminProfile,
        on_delete=models.PROTECT,
        related_name="assignments",
        verbose_name=_("Administrateur école"),
        help_text=_("Profil de l'administrateur école."),
    )
    school = models.ForeignKey(
        "school_operations.School",
        on_delete=models.PROTECT,
        related_name="admin_assignments",
        verbose_name=_("École"),
        help_text=_("École de rattachement."),
    )
    position = models.CharField(
        max_length=30,
        choices=SchoolAdminPosition.choices,
        verbose_name=_("Poste"),
        help_text=_("Poste occupé dans cette école."),
    )
    start_date = models.DateField(
        verbose_name=_("Date de début"),
        help_text=_("Date de début d'affectation."),
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de fin"),
        help_text=_("Date de fin (vide = affectation en cours)."),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("Affectation principale"),
        help_text=_("Affectation principale (utilisée par défaut pour ce school admin)."),
    )

    class Meta:
        db_table = "school_admin_assignment"
        verbose_name = _("Affectation admin école")
        verbose_name_plural = _("Affectations admin école")
        ordering = ["-start_date", "school__name"]
        indexes = [
            models.Index(fields=["school_admin", "school"], name="sa_assign_admin_school_idx"),
            models.Index(fields=["school", "end_date"], name="sa_assign_school_end_idx"),
        ]
        constraints = [
            # Une seule affectation active par (admin, école)
            models.UniqueConstraint(
                fields=["school_admin", "school"],
                condition=models.Q(is_deleted=False, end_date__isnull=True),
                name="unique_active_school_admin_assignment",
            ),
            # start_date < end_date quand end_date renseignée
            models.CheckConstraint(
                condition=(
                    models.Q(end_date__isnull=True)
                    | models.Q(start_date__lt=models.F("end_date"))
                ),
                name="school_admin_assignment_dates_valid",
            ),
            # Au plus une affectation principale active par school_admin
            models.UniqueConstraint(
                fields=["school_admin"],
                condition=models.Q(is_deleted=False, end_date__isnull=True, is_primary=True),
                name="unique_primary_school_admin_assignment",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.school_admin} → {self.school} ({self.get_position_display()})"

    def clean(self):
        super().clean()

        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError(
                {"end_date": _("La date de fin doit être postérieure à la date de début.")}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
