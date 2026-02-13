from rest_framework import serializers

from domain.school_operations.models import School


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model."""
    
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "code",
            "locality",
            "address",
            "phone",
            "email",
            "website",
            "founded_date",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
