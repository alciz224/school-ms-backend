"""
Serializers for user management.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

from domain.account.validators import validate_phone_number

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Basic user serializer."""

    full_name = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "full_name",
            "is_verified",
            "is_active",
        ]
        read_only_fields = fields


class UserDetailSerializer(serializers.ModelSerializer):
    """Detailed user serializer for profile."""

    full_name = serializers.CharField(read_only=True)
    masked_email = serializers.CharField(read_only=True)
    masked_phone = serializers.CharField(read_only=True)
    security_summary = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "masked_email",
            "masked_phone",
            "first_name",
            "last_name",
            "full_name",
            "email_verified",
            "email_verified_at",
            "phone_verified",
            "phone_verified_at",
            "is_verified",
            "backup_phone",
            "backup_phone_owner",
            "is_active",
            "date_joined",
            "last_login",
            "security_summary",
        ]
        read_only_fields = [
            "id",
            "email_verified",
            "email_verified_at",
            "phone_verified",
            "phone_verified_at",
            "is_verified",
            "is_active",
            "date_joined",
            "last_login",
        ]

    def get_security_summary(self, obj):
        return obj.get_security_summary()


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile."""

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "backup_phone",
            "backup_phone_owner",
        ]

    def validate_backup_phone(self, value):
        if value:
            try:
                value = validate_phone_number(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(str(e.message))

            # Cannot be same as primary phone
            user = self.instance
            if user and value == user.phone:
                raise serializers.ValidationError(
                    "Backup phone must be different from primary phone."
                )
        return value


class UserEmailUpdateSerializer(serializers.Serializer):
    """Serializer for updating email."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.lower().strip()
        user = self.context.get("user") or self.context["request"].user

        if value == (user.email or "").lower():
            raise serializers.ValidationError("This is already your email.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("This email is already in use.")

        return value

    def validate_password(self, value):
        user = self.context.get("user") or self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Invalid password.")
        return value


class UserPhoneUpdateSerializer(serializers.Serializer):
    """Serializer for updating phone."""

    phone = serializers.CharField(max_length=20)
    password = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        try:
            value = validate_phone_number(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e.message))

        user = self.context.get("user") or self.context["request"].user
        if value == user.phone:
            raise serializers.ValidationError("This is already your phone.")

        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("This phone is already in use.")

        return value

    def validate_password(self, value):
        user = self.context.get("user") or self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Invalid password.")
        return value
