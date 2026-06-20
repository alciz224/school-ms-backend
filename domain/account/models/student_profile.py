"""StudentProfile model."""

from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.account.constants import Gender
from domain.account.models.user import CustomUser
from domain.shared.models.base import AuditModel


class StudentProfile(AuditModel):
    """
    Profil élève — extension de CustomUser pour les utilisateurs ayant un rôle 'student'.

    Un StudentProfile ne peut pas exister sans CustomUser : c'est l'extension du
    compte utilisateur côté portail élève.

    Cas particulier : les élèves qui n'ont **pas** de compte plateforme (faute
    de téléphone) ne sont représentés QUE par leur StudentEnrollment (qui garde
    leurs nom/prénom en snapshot et a student=NULL). Ces élèves n'ont donc
    aucun StudentProfile.

    Règles métier :
        - user obligatoire et unique (OneToOne)
        - birth_cert_number unique quand renseigné
        - date_of_birth obligatoire et dans le passé
        - Si has_disability=False, disability_notes doit être vide
    """

    user = models.OneToOneField(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="student_profile",
        verbose_name=_("Compte utilisateur"),
        help_text=_("Compte utilisateur lié (obligatoire)."),
    )

    date_of_birth = models.DateField(
        verbose_name=_("Date de naissance"),
        help_text=_("Date de naissance."),
    )
    gender = models.CharField(
        max_length=1,
        choices=Gender.choices,
        verbose_name=_("Sexe"),
        help_text=_("Sexe (M/F)."),
    )
    place_of_birth = models.ForeignKey(
        "geography.Locality",
        on_delete=models.PROTECT,
        related_name="students_born_here",
        null=True,
        blank=True,
        verbose_name=_("Lieu de naissance"),
        help_text=_("Localité de naissance."),
    )
    birth_cert_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        verbose_name=_("Numéro d'acte de naissance"),
        help_text=_("Numéro d'acte de naissance."),
    )
    nationality = models.CharField(
        max_length=3,
        default="GN",
        verbose_name=_("Nationalité"),
        help_text=_("Code pays ISO (GN, ML, SN, CI...)."),
    )

    photo = models.ImageField(
        upload_to="profiles/students/",
        null=True,
        blank=True,
        verbose_name=_("Photo"),
        help_text=_("Photo d'identité."),
    )
    address = models.TextField(
        blank=True,
        verbose_name=_("Adresse"),
        help_text=_("Adresse de résidence."),
    )

    has_disability = models.BooleanField(
        default=False,
        verbose_name=_("Situation de handicap"),
        help_text=_("L'élève présente-t-il un handicap nécessitant un suivi ?"),
    )
    disability_notes = models.TextField(
        blank=True,
        verbose_name=_("Précisions sur le handicap"),
        help_text=_("Précisions sur le handicap (vide si has_disability=False)."),
    )

    class Meta:
        db_table = "student_profile"
        verbose_name = _("Profil élève")
        verbose_name_plural = _("Profils élèves")
        ordering = ["user__last_name", "user__first_name"]
        indexes = [
            models.Index(fields=["birth_cert_number"], name="student_profile_birth_cert_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["birth_cert_number"],
                condition=models.Q(is_deleted=False, birth_cert_number__isnull=False),
                name="unique_student_birth_cert_number",
            ),
        ]

    def __str__(self) -> str:
        return self.full_name

    @property
    def full_name(self) -> str:
        return f"{self.user.first_name} {self.user.last_name}".strip()

    def clean(self):
        super().clean()

        # Date de naissance dans le passé
        if self.date_of_birth and self.date_of_birth >= date.today():
            raise ValidationError(
                {"date_of_birth": _("La date de naissance doit être dans le passé.")}
            )

        # Notes de handicap seulement si has_disability=True
        if not self.has_disability and self.disability_notes.strip():
            raise ValidationError(
                {"disability_notes": _("Les notes de handicap ne sont autorisées que si has_disability=True.")}
            )

        # Si has_disability=True, des notes doivent être fournies
        if self.has_disability and not self.disability_notes.strip():
            raise ValidationError(
                {"disability_notes": _("Veuillez préciser le handicap dans les notes.")}
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
