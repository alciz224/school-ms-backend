# domain/accounts/api/serializers/verification.py

"""
Serializers pour la vérification.
"""

from rest_framework import serializers

from domain.accounts.constants import VerificationType


class SendVerificationCodeSerializer(serializers.Serializer):
    """Serializer pour envoyer un code de vérification."""

    type = serializers.ChoiceField(
        choices=[
            (VerificationType.EMAIL, "Email"),
            (VerificationType.PHONE, "Téléphone"),
        ],
        help_text="Type de vérification: 'email' ou 'phone'",
    )


class ConfirmVerificationCodeSerializer(serializers.Serializer):
    """Serializer pour confirmer un code de vérification."""

    type = serializers.ChoiceField(
        choices=[
            (VerificationType.EMAIL, "Email"),
            (VerificationType.PHONE, "Téléphone"),
        ]
    )
    code = serializers.CharField(
        min_length=6, max_length=6, help_text="Code de vérification à 6 chiffres"
    )

    def validate_code(self, value):
        # Nettoyer le code
        value = value.strip()
        if not value.isdigit():
            raise serializers.ValidationError(
                "Le code doit contenir uniquement des chiffres."
            )
        return value


class VerificationStatusSerializer(serializers.Serializer):
    """Serializer pour le statut de vérification (réponse)."""

    is_verified = serializers.BooleanField()
    email = serializers.DictField()
    phone = serializers.DictField()


class SendCodeResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse d'envoi de code."""

    sent_to = serializers.CharField()
    masked = serializers.CharField()
    expires_in = serializers.IntegerField()
    can_resend_in = serializers.IntegerField()
    dev_code = serializers.CharField(required=False, allow_null=True)


class VerifyCodeResponseSerializer(serializers.Serializer):
    """Serializer pour la réponse de vérification."""

    type = serializers.CharField()
    verified_at = serializers.DateTimeField()
    is_fully_verified = serializers.BooleanField()
    security = serializers.DictField()
