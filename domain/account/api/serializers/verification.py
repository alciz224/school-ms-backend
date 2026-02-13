"""
Serializers for verification.
"""

from rest_framework import serializers

from domain.account.constants import VerificationType, VerificationMethod


class SendVerificationCodeSerializer(serializers.Serializer):
    """Serializer for requesting a verification code."""

    type = serializers.ChoiceField(
        choices=VerificationMethod.choices,
        help_text="Type of verification: 'email' or 'phone'",
    )


class ConfirmVerificationCodeSerializer(serializers.Serializer):
    """Serializer for confirming a verification code."""

    type = serializers.ChoiceField(
        choices=VerificationMethod.choices,
        help_text="Type of verification: 'email' or 'phone'",
    )
    code = serializers.CharField(
        min_length=6, max_length=6, help_text="6-digit verification code"
    )

    def validate_code(self, value):
        return value.strip().upper()


class VerificationStatusSerializer(serializers.Serializer):
    """Serializer for verification status (response)."""

    is_verified = serializers.BooleanField()
    email = serializers.DictField()
    phone = serializers.DictField()
