from rest_framework import serializers

from domain.account.models import CustomUser


class SchoolAdminParentChildSerializer(serializers.Serializer):
    """Serializer for the nested children array in Parent."""
    id = serializers.CharField()
    full_name = serializers.CharField()
    class_name = serializers.CharField(default="")
    level = serializers.CharField(default="")
    academic_year = serializers.CharField(default="")
    enrollment_status = serializers.CharField(default="")


class SchoolAdminParentSerializer(serializers.ModelSerializer):
    """
    Serializer matching the frontend `Parent` interface for the school-admin portal.
    """
    id = serializers.CharField()
    full_name = serializers.CharField()
    address = serializers.SerializerMethodField()
    children_count = serializers.IntegerField(default=0)
    children = SchoolAdminParentChildSerializer(many=True, default=list)

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "full_name",
            "email",
            "phone",
            "address",
            "children_count",
            "children",
        ]

    def get_address(self, obj):
        # CustomUser does not have address natively, stub for frontend
        return None
