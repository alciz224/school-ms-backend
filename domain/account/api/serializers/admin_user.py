"""
Serializers for admin user management (super-admin portal).

Frontend source of truth: src/server/data/users/types.ts
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema_field

from domain.account.selectors.admin_user import AdminUserSelector

User = get_user_model()


class AdminUserListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for the user list endpoint.

    Matches frontend AdminUser type for array responses.
    """

    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "updated_at",
            "is_deleted",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.BooleanField())
    def get_is_deleted(self, obj):
        return not obj.is_active


class SchoolAdminSchoolEntrySerializer(serializers.Serializer):
    id = serializers.UUIDField()
    name = serializers.CharField()


class UserProfileEntrySerializer(serializers.Serializer):
    school_year_id = serializers.UUIDField()
    school_year_name = serializers.CharField()
    school_id = serializers.UUIDField()
    school_name = serializers.CharField()
    status = serializers.CharField()


class StudentEnrollmentEntrySerializer(serializers.Serializer):
    student_id = serializers.UUIDField()
    student_name = serializers.CharField()
    school_year = serializers.CharField(allow_null=True)
    level = serializers.CharField(allow_null=True)
    classroom = serializers.CharField(allow_null=True)
    status = serializers.CharField()


class ParentChildEntrySerializer(serializers.Serializer):
    student_name = serializers.CharField()
    school_year = serializers.CharField(allow_null=True)
    level = serializers.CharField(allow_null=True)
    classroom = serializers.CharField(allow_null=True)


class UserProfilesSerializer(serializers.Serializer):
    is_super_admin = serializers.BooleanField()
    school_admin_schools = SchoolAdminSchoolEntrySerializer(many=True)
    teacher_assignments = UserProfileEntrySerializer(many=True)
    student_enrollments = StudentEnrollmentEntrySerializer(many=True)
    parent_children = ParentChildEntrySerializer(many=True)


class AdminUserDetailSerializer(serializers.ModelSerializer):
    """Full user detail including profiles.

    Matches frontend UserDetail (AdminUser + UserProfiles).
    """

    is_deleted = serializers.SerializerMethodField()
    profiles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "phone",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "date_joined",
            "last_login",
            "updated_at",
            "is_deleted",
            "profiles",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.BooleanField())
    def get_is_deleted(self, obj):
        return not obj.is_active

    @extend_schema_field(UserProfilesSerializer())
    def get_profiles(self, obj):
        return AdminUserSelector.get_user_profiles(user=obj)


class AdminUserCreateResponseSerializer(AdminUserDetailSerializer):
    """Detail response with the generated password (create only)."""

    password = serializers.CharField(read_only=True)

    class Meta(AdminUserDetailSerializer.Meta):
        fields = AdminUserDetailSerializer.Meta.fields + ["password"]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["password"] = self.context.get("password", "")
        return data


class AdminUserCreateSerializer(serializers.Serializer):
    """Input serializer for creating a user.

    Matches frontend CreateAdminUserInput.
    """

    email = serializers.EmailField(required=False, allow_null=True, default=None)
    phone = serializers.CharField(max_length=20, required=False, allow_null=True, default=None)
    first_name = serializers.CharField(max_length=50)
    last_name = serializers.CharField(max_length=50)
    is_active = serializers.BooleanField(default=True)
    is_staff = serializers.BooleanField(default=False)

    def validate(self, attrs):
        if not attrs.get("email") and not attrs.get("phone"):
            raise serializers.ValidationError("An email or phone number is required.")
        return attrs


class AdminUserUpdateSerializer(serializers.Serializer):
    """Input serializer for updating a user.

    All fields are optional (PATCH semantics).
    """

    email = serializers.EmailField(required=False)
    phone = serializers.CharField(max_length=20, required=False)
    first_name = serializers.CharField(max_length=50, required=False)
    last_name = serializers.CharField(max_length=50, required=False)
    is_active = serializers.BooleanField(required=False)
    is_staff = serializers.BooleanField(required=False)
