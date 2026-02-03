"""
Serializers for session-based authentication (API v2).
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

from domain.account.validators import validate_phone_number, check_password_strength

User = get_user_model()


class SessionRegisterSerializer(serializers.Serializer):
    """Serializer for session-based registration."""

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
                raise serializers.ValidationError("This email is already in use.")
        return value

    def validate_phone(self, value):
        if value:
            try:
                value = validate_phone_number(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e.message))

            if User.objects.filter(phone=value).exists():
                raise serializers.ValidationError("This phone is already in use.")
        return value

    def validate_password(self, value):
        password_check = check_password_strength(value)
        if not password_check["is_strong"]:
            raise serializers.ValidationError(password_check["issues"])
        return value

    def validate(self, attrs):
        # At least one identifier required
        email = attrs.get("email")
        phone = attrs.get("phone")

        if not email and not phone:
            raise serializers.ValidationError(
                {
                    "email": ["An email or phone number is required."],
                    "phone": ["An email or phone number is required."],
                }
            )

        # Check passwords match
        if attrs.get("password") != attrs.get("password_confirm"):
            raise serializers.ValidationError(
                {"password_confirm": ["Passwords do not match."]}
            )

        return attrs


class SessionLoginSerializer(serializers.Serializer):
    """Serializer for session-based login."""

    identifier = serializers.CharField(help_text="Email or phone number")
    password = serializers.CharField(write_only=True)

    def validate_identifier(self, value):
        return value.strip()


class SessionLogoutSerializer(serializers.Serializer):
    """Serializer for session-based logout (no fields needed)."""
    pass
