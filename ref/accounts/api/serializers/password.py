# domain/accounts/api/serializers/password.py

"""
Serializers pour la gestion des mots de passe.
"""

from rest_framework import serializers

from domain.accounts.validators import check_password_strength


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer pour demander une réinitialisation."""

    identifier = serializers.CharField(help_text="Email ou numéro de téléphone")

    def validate_identifier(self, value):
        return value.strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer pour confirmer la réinitialisation."""

    identifier = serializers.CharField()
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_code(self, value):
        return value.strip()

    def validate_new_password(self, value):
        password_check = check_password_strength(value)
        if not password_check["is_strong"]:
            raise serializers.ValidationError(password_check["issues"])
        return value

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password_confirm": ["Les mots de passe ne correspondent pas."]}
            )
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer pour changer le mot de passe (connecté)."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_new_password(self, value):
        password_check = check_password_strength(value)
        if not password_check["is_strong"]:
            raise serializers.ValidationError(password_check["issues"])
        return value

    def validate(self, attrs):
        if attrs.get("new_password") != attrs.get("new_password_confirm"):
            raise serializers.ValidationError(
                {"new_password_confirm": ["Les mots de passe ne correspondent pas."]}
            )
        return attrs
