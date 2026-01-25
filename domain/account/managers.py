"""
Custom managers for CustomUser.
"""

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .validators import validate_phone_number


class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser.

    Allows user creation with email OR phone.
    """

    def _create_user(
        self,
        email: str = None,
        phone: str = None,
        password: str = None,
        **extra_fields,
    ):
        """
        Create and save a user.

        Args:
            email: Email address (optional if phone provided)
            phone: Phone number (optional if email provided)
            password: Password
            **extra_fields: Additional fields

        Returns:
            Created CustomUser instance

        Raises:
            ValidationError: If neither email nor phone is provided
        """
        # Validation: at least one identifier required
        if not email and not phone:
            raise ValidationError(
                _("An email or phone number is required."),
                code="no_identifier",
            )

        # Normalize email
        if email:
            email = self.normalize_email(email)

        # Normalize phone
        if phone:
            phone = validate_phone_number(phone)

        # Create user
        user = self.model(email=email, phone=phone, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_user(
        self,
        email: str = None,
        phone: str = None,
        password: str = None,
        **extra_fields,
    ):
        """Create a standard user."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, phone, password, **extra_fields)

    def create_superuser(
        self,
        email: str = None,
        phone: str = None,
        password: str = None,
        **extra_fields,
    ):
        """Create a superuser."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("phone_verified", True if phone else False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))

        return self._create_user(email, phone, password, **extra_fields)

    def get_by_identifier(self, identifier: str):
        """
        Get a user by email OR phone.

        Args:
            identifier: Email or phone number

        Returns:
            CustomUser instance or None
        """
        identifier = identifier.strip()

        # Detect if it's an email
        if "@" in identifier:
            return self.filter(email__iexact=identifier).first()

        # Otherwise, it's a phone
        try:
            normalized_phone = validate_phone_number(identifier)
            return self.filter(phone=normalized_phone).first()
        except ValidationError:
            return None

    def verified(self):
        """Return verified users."""
        return self.filter(
            models.Q(email_verified=True) | models.Q(phone_verified=True)
        )

    def unverified(self):
        """Return unverified users."""
        return self.filter(email_verified=False, phone_verified=False)

    def with_security_score(self):
        """
        Annotate users with their security score.
        Note: Simplified calculation, real calculation is in the model.
        """
        return self.annotate(
            has_both_contacts=models.Case(
                models.When(
                    email__isnull=False, phone__isnull=False, then=models.Value(True)
                ),
                default=models.Value(False),
                output_field=models.BooleanField(),
            )
        )
