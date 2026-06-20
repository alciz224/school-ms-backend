"""TeacherProfile model."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.account.constants import DiplomaLevel, EmploymentType, Gender
from domain.account.models.user import CustomUser
from domain.shared.models.base import AuditModel


class TeacherProfile(AuditModel):
    """
    Profil enseignant.

    Contrairement au profil élève, l'enseignant doit obligatoirement avoir un
    CustomUser pour accéder au portail enseignant.

    Règles métier :
        - user obligatoire et unique (OneToOne)
        - employee_id (matricule fonctionnaire MEN) unique quand renseigné
        - diploma obligatoire (niveau minimum requis pour enseigner)
        - date_of_birth doit indiquer ≥ 18 ans
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="teacher_profile",
        verbose_name=_("Compte utilisateur"),
        help_text=_("Compte utilisateur lié."),
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Date de naissance"),
        help_text=_("Date de naissance."),
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        verbose_name=_("Sexe"),
        help_text=_("Sexe."),
    )

    employee_id = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("Matricule fonctionnaire"),
        help_text=_("Matricule fonctionnaire (MEN) si applicable."),
    )
    diploma = models.CharField(
        max_length=20,
        choices=DiplomaLevel.choices,
        verbose_name=_("Diplôme"),
        help_text=_("Niveau de diplôme le plus élevé."),
    )
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.CONTRACTUEL,
        verbose_name=_("Statut d'emploi"),
        help_text=_("Statut d'emploi (fonctionnaire, contractuel, vacataire...)."),
    )

    photo = models.ImageField(
        upload_to="profiles/teachers/",
        null=True,
        blank=True,
        verbose_name=_("Photo"),
    )
    address = models.TextField(
        blank=True,
        verbose_name=_("Adresse"),
        help_text=_("Adresse de résidence."),
    )

    class Meta:
        db_table = "teacher_profile"
        verbose_name = _("Profil enseignant")
        verbose_name_plural = _("Profils enseignants")
        ordering = ["user__last_name", "user__first_name"]
        indexes = [
            models.Index(fields=["employee_id"], name="teacher_profile_employee_idx"),
            models.Index(fields=["diploma"], name="teacher_profile_diploma_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["employee_id"],
                condition=models.Q(is_deleted=False, employee_id__isnull=False),
                name="unique_teacher_employee_id",
            ),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def clean(self):
        super().clean()

        if self.date_of_birth:
            today = date.today()
            if self.date_of_birth >= today:
                raise ValidationError(
                    {"date_of_birth": _("La date de naissance doit être dans le passé.")}
                )
            age = today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
            if age < 18:
                raise ValidationError(
                    {"date_of_birth": _("L'enseignant doit avoir au moins 18 ans.")}
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
