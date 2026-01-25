# domain/accounts/api/serializers/auth.py

"""
Serializers pour l'authentification.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from domain.accounts.validators import validate_phone_number, check_password_strength

User = get_user_model()


class RegisterSerializer(serializers.Serializer):
    """Serializer pour l'inscription."""

    email = serializers.EmailField(required=False, allow_null=True, allow_blank=True)
    phone = serializers.CharField(
        required=False, allow_null=True, allow_blank=True, max_length=20
    )
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(min_length=2, max_length=50)
    last_name = serializers.CharField(min_length=2, max_length=50)

    def validate_email(self, value):
        if value:
            value = value.lower().strip()
            if User.objects.filter(email__iexact=value).exists():
                raise serializers.ValidationError("Cet email est déjà utilisé.")
        return value

    def validate_phone(self, value):
        if value:
            try:
                value = validate_phone_number(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e.message))

            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError("Ce numéro est déjà utilisé.")
        return value

    def validate_password(self, value):
        password_check = check_password_strength(value)
        if not password_check["is_strong"]:
            raise serializers.ValidationError(password_check["issues"])
        return value

    def validate(self, attrs):
        # Au moins un identifiant requis
        email = attrs.get("email")
        phone = attrs.get("phone")

        if not email and not phone:
            raise serializers.ValidationError(
                {
                    "email": ["Un email ou un numéro de téléphone est requis."],
                    "phone": ["Un email ou un numéro de téléphone est requis."],
                }
            )

        # Vérifier que les mots de passe correspondent
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": ["Les mots de passe ne correspondent pas."]}
            )

        return attrs


class LoginSerializer(serializers.Serializer):
    """Serializer pour la connexion."""

    identifier = serializers.CharField(help_text="Email ou numéro de téléphone")
    password = serializers.CharField(write_only=True)

    def validate_identifier(self, value):
        return value.strip()


class LogoutSerializer(serializers.Serializer):
    """Serializer pour la déconnexion."""

    refresh = serializers.CharField(help_text="Refresh token à invalider")


class TokenRefreshSerializer(serializers.Serializer):
    """Serializer pour rafraîchir les tokens."""

    refresh = serializers.CharField()


class TokenPairSerializer(serializers.Serializer):
    """Serializer pour la paire de tokens (réponse)."""

    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)
