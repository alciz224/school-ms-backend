# apps/accounts/managers.py

"""
Managers personnalisés pour CustomUser.
"""

from django.contrib.auth.models import BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .validators import validate_phone_number


class CustomUserManager(BaseUserManager):
    """
    Manager personnalisé pour CustomUser.

    Permet la création d'utilisateurs avec email OU téléphone.
    """

    def _create_user(
        self, email: str = None, phone: str = None, password: str = None, **extra_fields
    ):
        """
        Crée et sauvegarde un utilisateur.

        Args:
            email: Adresse email (optionnel si phone fourni)
            phone: Numéro de téléphone (optionnel si email fourni)
            password: Mot de passe
            **extra_fields: Champs supplémentaires

        Returns:
            Instance CustomUser créée

        Raises:
            ValidationError: Si ni email ni phone n'est fourni
        """
        # Validation: au moins un identifiant requis
        if not email and not phone:
            raise ValidationError(
                _("Un email ou un numéro de téléphone est requis."),
                code="no_identifier",
            )

        # Normaliser email
        if email:
            email = self.normalize_email(email)

        # Normaliser téléphone
        if phone:
            phone = validate_phone_number(phone)

        # Créer l'utilisateur
        user = self.model(email=email, phone=phone, **extra_fields)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.full_clean()
        user.save(using=self._db)

        return user

    def create_user(
        self, email: str = None, phone: str = None, password: str = None, **extra_fields
    ):
        """Crée un utilisateur standard."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, phone, password, **extra_fields)

    def create_superuser(
        self, email: str = None, phone: str = None, password: str = None, **extra_fields
    ):
        """Crée un superutilisateur."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("email_verified", True)
        extra_fields.setdefault("phone_verified", True if phone else False)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Le superuser doit avoir is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Le superuser doit avoir is_superuser=True."))

        return self._create_user(email, phone, password, **extra_fields)

    def get_by_identifier(self, identifier: str):
        """
        Récupère un utilisateur par email OU téléphone.

        Args:
            identifier: Email ou numéro de téléphone

        Returns:
            Instance CustomUser ou None
        """
        identifier = identifier.strip()

        # Détecter si c'est un email
        if "@" in identifier:
            return self.filter(email__iexact=identifier).first()

        # Sinon, c'est un téléphone
        try:
            normalized_phone = validate_phone_number(identifier)
            return self.filter(phone=normalized_phone).first()
        except ValidationError:
            return None

    def verified(self):
        """Retourne les utilisateurs vérifiés."""
        return self.filter(
            models.Q(email_verified=True) | models.Q(phone_verified=True)
        )

    def unverified(self):
        """Retourne les utilisateurs non vérifiés."""
        return self.filter(email_verified=False, phone_verified=False)

    def with_security_score(self):
        """
        Annote les utilisateurs avec leur score de sécurité.
        Note: Calcul simplifié, le vrai calcul est dans le model.
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
