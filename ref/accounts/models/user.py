# apps/accounts/models/user.py

"""
Modèle CustomUser - Utilisateur personnalisé indépendant.
"""

import uuid
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from django.conf import settings
from django.db.models import Q
from ..managers import CustomUserManager
from ..validators import validate_phone_number
from ..constants import SecurityLevel


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Utilisateur personnalisé avec authentification flexible.

    Peut s'authentifier avec:
        - Email + mot de passe
        - Téléphone + mot de passe

    Le compte est indépendant des profils (Student, Teacher, etc.)
    qui sont créés séparément et liés à cet utilisateur.
    """

    # ==========================================================================
    # IDENTIFIANTS
    # ==========================================================================

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("ID")
    )

    email = models.EmailField(
        verbose_name=_("Adresse email"),
        max_length=254,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Adresse email pour la connexion et les notifications."),
    )

    phone = models.CharField(
        verbose_name=_("Téléphone"),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        validators=[validate_phone_number],
        help_text=_("Numéro de téléphone au format international (+224...)."),
    )

    # ==========================================================================
    # INFORMATIONS PERSONNELLES
    # ==========================================================================

    first_name = models.CharField(verbose_name=_("Prénom"), max_length=50)

    last_name = models.CharField(verbose_name=_("Nom"), max_length=50)

    # ==========================================================================
    # VÉRIFICATION
    # ==========================================================================

    email_verified = models.BooleanField(
        verbose_name=_("Email vérifié"),
        default=False,
        help_text=_("Indique si l'email a été vérifié."),
    )

    email_verified_at = models.DateTimeField(
        verbose_name=_("Date vérification email"), null=True, blank=True
    )

    phone_verified = models.BooleanField(
        verbose_name=_("Téléphone vérifié"),
        default=False,
        help_text=_("Indique si le téléphone a été vérifié."),
    )

    phone_verified_at = models.DateTimeField(
        verbose_name=_("Date vérification téléphone"), null=True, blank=True
    )

    # ==========================================================================
    # CONTACT DE SECOURS
    # ==========================================================================

    backup_phone = models.CharField(
        verbose_name=_("Téléphone de secours"),
        max_length=20,
        null=True,
        blank=True,
        validators=[validate_phone_number],
        help_text=_("Numéro d'un proche pour récupération de compte."),
    )

    backup_phone_owner = models.CharField(
        verbose_name=_("Propriétaire du téléphone de secours"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("Nom du propriétaire (ex: 'Maman', 'Papa', 'Oncle Ibrahima')."),
    )

    # ==========================================================================
    # STATUT
    # ==========================================================================

    is_active = models.BooleanField(
        verbose_name=_("Actif"),
        default=True,
        help_text=_("Indique si le compte est actif."),
    )

    is_staff = models.BooleanField(
        verbose_name=_("Staff"),
        default=False,
        help_text=_("Peut accéder à l'administration Django."),
    )

    # ==========================================================================
    # MÉTADONNÉES
    # ==========================================================================

    date_joined = models.DateTimeField(
        verbose_name=_("Date d'inscription"), default=timezone.now
    )

    last_login = models.DateTimeField(
        verbose_name=_("Dernière connexion"), null=True, blank=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Dernière modification"), auto_now=True
    )

    # ==========================================================================
    # CONFIGURATION
    # ==========================================================================

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Champ par défaut, mais on gère aussi phone
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("Utilisateur")
        verbose_name_plural = _("Utilisateurs")
        ordering = ["-date_joined"]

        constraints = [
            # Au moins un identifiant requics
            models.CheckConstraint(
                condition=~Q(email__isnull=True, phone__isnull=True),
                name="user_must_have_email_or_phone",
                violation_error_message=_("Un email ou un téléphone est requis."),
            ),
        ]

        indexes = [
            models.Index(fields=["email", "is_active"]),
            models.Index(fields=["phone", "is_active"]),
            models.Index(fields=["date_joined"]),
        ]

    def __str__(self):
        return self.full_name or self.identifier

    # ==========================================================================
    # PROPRIÉTÉS
    # ==========================================================================

    @property
    def full_name(self) -> str:
        """Retourne le nom complet."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def identifier(self) -> str:
        """Retourne l'identifiant principal (email ou phone)."""
        return self.email or self.phone or str(self.id)

    @property
    def masked_email(self) -> str | None:
        """Retourne l'email masqué pour l'affichage sécurisé."""
        if not self.email:
            return None

        local, domain = self.email.split("@")
        if len(local) <= 2:
            masked_local = local[0] + "*"
        else:
            masked_local = local[0] + "*" * (len(local) - 2) + local[-1]

        return f"{masked_local}@{domain}"

    @property
    def masked_phone(self) -> str | None:
        """Retourne le téléphone masqué pour l'affichage sécurisé."""
        if not self.phone:
            return None

        # +224620123456 -> +224 6XX-XXX-456
        if len(self.phone) > 6:
            return f"{self.phone[:5]} {'X' * (len(self.phone) - 8)}-{self.phone[-3:]}"
        return self.phone

    @property
    def is_verified(self) -> bool:
        """Le compte est vérifié si au moins un contact est vérifié."""
        return self.email_verified or self.phone_verified

    @property
    def verified_at(self) -> timezone.datetime | None:
        """Date de première vérification."""
        dates = [
            d for d in [self.email_verified_at, self.phone_verified_at] if d is not None
        ]
        return min(dates) if dates else None

    @property
    def has_email(self) -> bool:
        return bool(self.email)

    @property
    def has_phone(self) -> bool:
        return bool(self.phone)

    @property
    def has_backup_phone(self) -> bool:
        return bool(self.backup_phone)

    @property
    def has_both_contacts(self) -> bool:
        """A les deux moyens de contact."""
        return self.has_email and self.has_phone

    @property
    def security_questions_count(self) -> int:
        """Nombre de questions de sécurité configurées."""
        return self.security_questions.count()

    @property
    def has_security_questions(self) -> bool:
        """Au moins une question de sécurité configurée."""
        return self.security_questions_count > 0

    # ==========================================================================
    # SCORE DE SÉCURITÉ
    # ==========================================================================

    @property
    def security_score(self) -> int:
        """
        Calcule le score de sécurité du compte (0-100).
        """
        config = getattr(settings, "ACCOUNTS_CONFIG", {})
        weights = config.get(
            "SECURITY_SCORE_WEIGHTS",
            {
                "email_present": 10,
                "email_verified": 15,
                "phone_present": 10,
                "phone_verified": 15,
                "backup_phone": 15,
                "security_question": 10,
                "strong_password": 5,
            },
        )

        score = 0

        # Email
        if self.email:
            score += weights.get("email_present", 10)
        if self.email_verified:
            score += weights.get("email_verified", 15)

        # Téléphone
        if self.phone:
            score += weights.get("phone_present", 10)
        if self.phone_verified:
            score += weights.get("phone_verified", 15)

        # Contact de secours
        if self.backup_phone:
            score += weights.get("backup_phone", 15)

        # Questions de sécurité (max 3)
        questions_count = min(self.security_questions_count, 3)
        score += questions_count * weights.get("security_question", 10)

        return min(score, 100)

    @property
    def security_level(self) -> str:
        """Niveau de sécurité basé sur le score."""
        score = self.security_score

        if score >= 70:
            return SecurityLevel.HIGH
        elif score >= 40:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW

    @property
    def security_suggestions(self) -> list[str]:
        """Suggestions pour améliorer la sécurité."""
        suggestions = []

        if not self.email:
            suggestions.append("Ajoutez une adresse email")
        elif not self.email_verified:
            suggestions.append("Vérifiez votre adresse email")

        if not self.phone:
            suggestions.append("Ajoutez un numéro de téléphone")
        elif not self.phone_verified:
            suggestions.append("Vérifiez votre numéro de téléphone")

        if not self.backup_phone:
            suggestions.append("Ajoutez un contact de secours")

        if self.security_questions_count < 3:
            remaining = 3 - self.security_questions_count
            suggestions.append(f"Configurez {remaining} question(s) de sécurité")

        return suggestions

    def get_security_summary(self) -> dict:
        """Résumé complet de la sécurité pour l'API."""
        return {
            "score": self.security_score,
            "level": self.security_level,
            "is_verified": self.is_verified,
            "has_email": self.has_email,
            "email_verified": self.email_verified,
            "has_phone": self.has_phone,
            "phone_verified": self.phone_verified,
            "has_backup_phone": self.has_backup_phone,
            "security_questions_count": self.security_questions_count,
            "has_security_questions": self.has_security_questions,
            "suggestions": self.security_suggestions,
        }

    # ==========================================================================
    # MÉTHODES DE VÉRIFICATION
    # ==========================================================================

    def verify_email(self, save: bool = True) -> None:
        """Marque l'email comme vérifié."""
        if not self.email:
            raise ValidationError(_("Aucun email à vérifier."))

        self.email_verified = True
        self.email_verified_at = timezone.now()

        if save:
            self.save(
                update_fields=["email_verified", "email_verified_at", "updated_at"]
            )

    def verify_phone(self, save: bool = True) -> None:
        """Marque le téléphone comme vérifié."""
        if not self.phone:
            raise ValidationError(_("Aucun téléphone à vérifier."))

        self.phone_verified = True
        self.phone_verified_at = timezone.now()

        if save:
            self.save(
                update_fields=["phone_verified", "phone_verified_at", "updated_at"]
            )

    def unverify_email(self, save: bool = True) -> None:
        """Retire la vérification de l'email (après changement)."""
        self.email_verified = False
        self.email_verified_at = None

        if save:
            self.save(
                update_fields=["email_verified", "email_verified_at", "updated_at"]
            )

    def unverify_phone(self, save: bool = True) -> None:
        """Retire la vérification du téléphone (après changement)."""
        self.phone_verified = False
        self.phone_verified_at = None

        if save:
            self.save(
                update_fields=["phone_verified", "phone_verified_at", "updated_at"]
            )

    # ==========================================================================
    # MÉTHODES DE MISE À JOUR
    # ==========================================================================

    def update_email(self, new_email: str, save: bool = True) -> None:
        """
        Met à jour l'email et retire la vérification.
        """
        if new_email:
            new_email = CustomUserManager().normalize_email(new_email)

        if new_email == self.email:
            return

        self.email = new_email
        self.unverify_email(save=False)

        if save:
            self.save(
                update_fields=[
                    "email",
                    "email_verified",
                    "email_verified_at",
                    "updated_at",
                ]
            )

    def update_phone(self, new_phone: str, save: bool = True) -> None:
        """
        Met à jour le téléphone et retire la vérification.
        Garde l'historique de l'ancien numéro.
        """
        if new_phone:
            new_phone = validate_phone_number(new_phone)

        if new_phone == self.phone:
            return

        # Sauvegarder l'ancien dans l'historique
        if self.phone:
            from .history import PhoneHistory
            from ..constants import PhoneRemovalReason

            PhoneHistory.objects.create(
                user=self,
                phone=self.phone,
                verified=self.phone_verified,
                reason=PhoneRemovalReason.CHANGED,
            )

        self.phone = new_phone
        self.unverify_phone(save=False)

        if save:
            self.save(
                update_fields=[
                    "phone",
                    "phone_verified",
                    "phone_verified_at",
                    "updated_at",
                ]
            )

    # ==========================================================================
    # VALIDATION
    # ==========================================================================

    def clean(self):
        """Validation du modèle."""
        super().clean()

        # Vérifier qu'au moins un identifiant est présent
        if not self.email and not self.phone:
            raise ValidationError(
                _("Un email ou un numéro de téléphone est requis."),
                code="no_identifier",
            )

        # Normaliser le téléphone
        if self.phone:
            self.phone = validate_phone_number(self.phone)

        # Normaliser le téléphone de secours
        if self.backup_phone:
            self.backup_phone = validate_phone_number(self.backup_phone)

            # Le backup ne peut pas être le même que le principal
            if self.backup_phone == self.phone:
                raise ValidationError(
                    _("Le téléphone de secours doit être différent du principal."),
                    code="same_backup_phone",
                )

    def save(self, *args, **kwargs):
        """Sauvegarde avec normalisation."""
        # Normaliser l'email
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

        self.full_clean()
        super().save(*args, **kwargs)
