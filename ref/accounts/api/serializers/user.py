# domain/accounts/api/serializers/user.py

"""
Serializers pour le profil utilisateur.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError

from domain.accounts.validators import validate_phone_number

User = get_user_model()


class SecuritySummarySerializer(serializers.Serializer):
    """Serializer pour le résumé de sécurité."""

    score = serializers.IntegerField(read_only=True)
    level = serializers.CharField(read_only=True)
    has_security_questions = serializers.BooleanField(read_only=True)
    security_questions_count = serializers.IntegerField(read_only=True)
    has_backup_phone = serializers.BooleanField(read_only=True)
    suggestions = serializers.ListField(child=serializers.CharField(), read_only=True)


class VerificationSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé de vérification."""

    is_verified = serializers.BooleanField(read_only=True)
    email_verified = serializers.BooleanField(read_only=True)
    email_verified_at = serializers.DateTimeField(read_only=True, allow_null=True)
    phone_verified = serializers.BooleanField(read_only=True)
    phone_verified_at = serializers.DateTimeField(read_only=True, allow_null=True)


class ProfilesSummarySerializer(serializers.Serializer):
    """Serializer pour le résumé des profils."""

    has_student = serializers.BooleanField(read_only=True)
    has_teacher = serializers.BooleanField(read_only=True)
    has_school_admin = serializers.BooleanField(read_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Serializer complet pour l'utilisateur."""

    full_name = serializers.CharField(read_only=True)
    email_masked = serializers.CharField(source="masked_email", read_only=True)
    phone_masked = serializers.CharField(source="masked_phone", read_only=True)

    verification = serializers.SerializerMethodField()
    security = serializers.SerializerMethodField()
    profiles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "email_masked",
            "phone",
            "phone_masked",
            "first_name",
            "last_name",
            "full_name",
            "backup_phone",
            "backup_phone_owner",
            "verification",
            "security",
            "profiles",
            "date_joined",
            "last_login",
        ]
        read_only_fields = [
            "id",
            "email",
            "phone",
            "date_joined",
            "last_login",
        ]

    def get_verification(self, obj) -> dict:
        return {
            "is_verified": obj.is_verified,
            "email_verified": obj.email_verified,
            "email_verified_at": (
                obj.email_verified_at.isoformat() if obj.email_verified_at else None
            ),
            "phone_verified": obj.phone_verified,
            "phone_verified_at": (
                obj.phone_verified_at.isoformat() if obj.phone_verified_at else None
            ),
        }

    def get_security(self, obj) -> dict:
        return obj.get_security_summary()

    def get_profiles(self, obj) -> dict:
        # TODO: Implémenter quand les profils seront créés
        return {
            "has_student": (
                hasattr(obj, "student_profiles") and obj.student_profiles.exists()
                if hasattr(obj, "student_profiles")
                else False
            ),
            "has_teacher": (
                hasattr(obj, "teacher_profiles") and obj.teacher_profiles.exists()
                if hasattr(obj, "teacher_profiles")
                else False
            ),
            "has_school_admin": (
                hasattr(obj, "school_admin_profiles")
                and obj.school_admin_profiles.exists()
                if hasattr(obj, "school_admin_profiles")
                else False
            ),
        }


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer pour la mise à jour du profil."""

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

            # Le backup ne peut pas être le même que le principal
            if self.instance and value == self.instance.phone:
                raise serializers.ValidationError(
                    "Le téléphone de secours doit être différent du principal."
                )
        return value


class UserEmailUpdateSerializer(serializers.Serializer):
    """Serializer pour modifier l'email."""

    email = serializers.EmailField()
    current_password = serializers.CharField(write_only=True)

    def validate_email(self, value):
        value = value.lower().strip()
        user = self.context.get("user")

        if user and value == user.email:
            raise serializers.ValidationError("C'est déjà votre email actuel.")

        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("Cet email est déjà utilisé.")

        return value

    def validate_current_password(self, value):
        user = self.context.get("user")
        if user and not user.check_password(value):
            raise serializers.ValidationError("Mot de passe incorrect.")
        return value


class UserPhoneUpdateSerializer(serializers.Serializer):
    """Serializer pour modifier le téléphone."""

    phone = serializers.CharField(max_length=20)
    current_password = serializers.CharField(write_only=True)

    def validate_phone(self, value):
        try:
            value = validate_phone_number(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(str(e.message))

        user = self.context.get("user")

        if user and value == user.phone:
            raise serializers.ValidationError("C'est déjà votre numéro actuel.")

        if User.objects.filter(phone=value).exists():
            raise serializers.ValidationError("Ce numéro est déjà utilisé.")

        return value

    def validate_current_password(self, value):
        user = self.context.get("user")
        if user and not user.check_password(value):
            raise serializers.ValidationError("Mot de passe incorrect.")
        return value
