"""
Serializers for password management.
"""

from rest_framework import serializers

from domain.account.validators import check_password_strength


class PasswordResetRequestSerializer(serializers.Serializer):
    """Serializer for requesting password reset."""

    identifier = serializers.CharField(help_text="Email or phone number")

    def validate_identifier(self, value):
        return value.strip()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Serializer for confirming password reset."""

    identifier = serializers.CharField(help_text="Email or phone number")
    code = serializers.CharField(min_length=6, max_length=6)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_identifier(self, value):
        return value.strip()

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
                {"new_password_confirm": ["Passwords do not match."]}
            )
        return attrs


class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for changing password (logged in user)."""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_current_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

    def validate_new_password(self, value):
        password_check = check_password_strength(value)
        if not password_check["is_strong"]:
            raise serializers.ValidationError(password_check["issues"])
        return value

    def validate(self, attrs):
        if attrs["new_password"] != attrs["new_password_confirm"]:
            raise serializers.ValidationError(
                {"new_password_confirm": ["Passwords do not match."]}
            )

        if attrs["current_password"] == attrs["new_password"]:
            raise serializers.ValidationError(
                {"new_password": ["New password must be different from current password."]}
            )

        return attrs


class PasswordStrengthSerializer(serializers.Serializer):
    """Serializer for checking password strength."""

    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        result = check_password_strength(attrs["password"])
        return result
