"""
CustomUser model - Independent custom user.
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
    Custom user with flexible authentication.

    Can authenticate with:
        - Email + password
        - Phone + password

    The account is independent of profiles (Student, Teacher, etc.)
    which are created separately and linked to this user.
    """

    # ==========================================================================
    # IDENTIFIERS
    # ==========================================================================

    id = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False, verbose_name=_("ID")
    )

    email = models.EmailField(
        verbose_name=_("Email address"),
        max_length=254,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Email address for login and notifications."),
    )

    phone = models.CharField(
        verbose_name=_("Phone"),
        max_length=20,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        validators=[validate_phone_number],
        help_text=_("Phone number in international format (+224...)."),
    )

    # ==========================================================================
    # PERSONAL INFORMATION
    # ==========================================================================

    first_name = models.CharField(verbose_name=_("First name"), max_length=50)

    last_name = models.CharField(verbose_name=_("Last name"), max_length=50)

    # ==========================================================================
    # VERIFICATION
    # ==========================================================================

    email_verified = models.BooleanField(
        verbose_name=_("Email verified"),
        default=False,
        help_text=_("Indicates if the email has been verified."),
    )

    email_verified_at = models.DateTimeField(
        verbose_name=_("Email verification date"), null=True, blank=True
    )

    phone_verified = models.BooleanField(
        verbose_name=_("Phone verified"),
        default=False,
        help_text=_("Indicates if the phone has been verified."),
    )

    phone_verified_at = models.DateTimeField(
        verbose_name=_("Phone verification date"), null=True, blank=True
    )

    # ==========================================================================
    # BACKUP CONTACT
    # ==========================================================================

    backup_phone = models.CharField(
        verbose_name=_("Backup phone"),
        max_length=20,
        null=True,
        blank=True,
        validators=[validate_phone_number],
        help_text=_("Phone number of a relative for account recovery."),
    )

    backup_phone_owner = models.CharField(
        verbose_name=_("Backup phone owner"),
        max_length=100,
        null=True,
        blank=True,
        help_text=_("Owner's name (e.g., 'Mom', 'Dad', 'Uncle John')."),
    )

    # ==========================================================================
    # STATUS
    # ==========================================================================

    is_active = models.BooleanField(
        verbose_name=_("Active"),
        default=True,
        help_text=_("Indicates if the account is active."),
    )

    is_staff = models.BooleanField(
        verbose_name=_("Staff"),
        default=False,
        help_text=_("Can access Django admin."),
    )

    # ==========================================================================
    # METADATA
    # ==========================================================================

    date_joined = models.DateTimeField(
        verbose_name=_("Date joined"), default=timezone.now
    )

    last_login = models.DateTimeField(
        verbose_name=_("Last login"), null=True, blank=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Last modified"), auto_now=True
    )

    # ==========================================================================
    # CONFIGURATION
    # ==========================================================================

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Default field, but we also handle phone
    REQUIRED_FIELDS = ["first_name", "last_name"]

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ["-date_joined"]

        constraints = [
            # At least one identifier required
            models.CheckConstraint(
                condition=~Q(email__isnull=True, phone__isnull=True),
                name="user_must_have_email_or_phone",
                violation_error_message=_("An email or phone is required."),
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
    # PROPERTIES
    # ==========================================================================

    @property
    def full_name(self) -> str:
        """Return full name."""
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def identifier(self) -> str:
        """Return primary identifier (email or phone)."""
        return self.email or self.phone or str(self.id)

    @property
    def masked_email(self) -> str | None:
        """Return masked email for secure display."""
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
        """Return masked phone for secure display."""
        if not self.phone:
            return None

        # +224620123456 -> +224 6XX-XXX-456
        if len(self.phone) > 6:
            return f"{self.phone[:5]} {'X' * (len(self.phone) - 8)}-{self.phone[-3:]}"
        return self.phone

    @property
    def is_verified(self) -> bool:
        """Account is verified if at least one contact is verified."""
        return self.email_verified or self.phone_verified

    @property
    def verified_at(self) -> timezone.datetime | None:
        """Date of first verification."""
        dates = [
            d
            for d in [self.email_verified_at, self.phone_verified_at]
            if d is not None
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
        """Has both contact methods."""
        return self.has_email and self.has_phone

    @property
    def security_questions_count(self) -> int:
        """Number of configured security questions."""
        return self.security_questions.count()

    @property
    def has_security_questions(self) -> bool:
        """At least one security question configured."""
        return self.security_questions_count > 0

    # ==========================================================================
    # SECURITY SCORE
    # ==========================================================================

    @property
    def security_score(self) -> int:
        """
        Calculate account security score (0-100).
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

        # Phone
        if self.phone:
            score += weights.get("phone_present", 10)
        if self.phone_verified:
            score += weights.get("phone_verified", 15)

        # Backup contact
        if self.backup_phone:
            score += weights.get("backup_phone", 15)

        # Security questions (max 3)
        questions_count = min(self.security_questions_count, 3)
        score += questions_count * weights.get("security_question", 10)

        return min(score, 100)

    @property
    def security_level(self) -> str:
        """Security level based on score."""
        score = self.security_score

        if score >= 70:
            return SecurityLevel.HIGH
        elif score >= 40:
            return SecurityLevel.MEDIUM
        else:
            return SecurityLevel.LOW

    @property
    def security_suggestions(self) -> list[str]:
        """Suggestions to improve security."""
        suggestions = []

        if not self.email:
            suggestions.append("Add an email address")
        elif not self.email_verified:
            suggestions.append("Verify your email address")

        if not self.phone:
            suggestions.append("Add a phone number")
        elif not self.phone_verified:
            suggestions.append("Verify your phone number")

        if not self.backup_phone:
            suggestions.append("Add a backup contact")

        if self.security_questions_count < 3:
            remaining = 3 - self.security_questions_count
            suggestions.append(f"Configure {remaining} security question(s)")

        return suggestions

    def get_security_summary(self) -> dict:
        """Complete security summary for API."""
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
    # VERIFICATION METHODS
    # ==========================================================================

    def verify_email(self, save: bool = True) -> None:
        """Mark email as verified."""
        if not self.email:
            raise ValidationError(_("No email to verify."))

        self.email_verified = True
        self.email_verified_at = timezone.now()

        if save:
            self.save(
                update_fields=["email_verified", "email_verified_at", "updated_at"]
            )

    def verify_phone(self, save: bool = True) -> None:
        """Mark phone as verified."""
        if not self.phone:
            raise ValidationError(_("No phone to verify."))

        self.phone_verified = True
        self.phone_verified_at = timezone.now()

        if save:
            self.save(
                update_fields=["phone_verified", "phone_verified_at", "updated_at"]
            )

    def unverify_email(self, save: bool = True) -> None:
        """Remove email verification (after change)."""
        self.email_verified = False
        self.email_verified_at = None

        if save:
            self.save(
                update_fields=["email_verified", "email_verified_at", "updated_at"]
            )

    def unverify_phone(self, save: bool = True) -> None:
        """Remove phone verification (after change)."""
        self.phone_verified = False
        self.phone_verified_at = None

        if save:
            self.save(
                update_fields=["phone_verified", "phone_verified_at", "updated_at"]
            )

    # ==========================================================================
    # UPDATE METHODS
    # ==========================================================================

    def update_email(self, new_email: str, save: bool = True) -> None:
        """
        Update email and remove verification.
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
        Update phone and remove verification.
        Keeps history of the old number.
        """
        if new_phone:
            new_phone = validate_phone_number(new_phone)

        if new_phone == self.phone:
            return

        # Save old number to history
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
        """Model validation."""
        super().clean()

        # Check at least one identifier is present
        if not self.email and not self.phone:
            raise ValidationError(
                _("An email or phone number is required."),
                code="no_identifier",
            )

        # Normalize phone
        if self.phone:
            self.phone = validate_phone_number(self.phone)

        # Normalize backup phone
        if self.backup_phone:
            self.backup_phone = validate_phone_number(self.backup_phone)

            # Backup cannot be the same as primary
            if self.backup_phone == self.phone:
                raise ValidationError(
                    _("The backup phone must be different from the primary."),
                    code="same_backup_phone",
                )

    def save(self, *args, **kwargs):
        """Save with normalization."""
        # Normalize email
        if self.email:
            self.email = self.__class__.objects.normalize_email(self.email)

        self.full_clean()
        super().save(*args, **kwargs)
