from rest_framework import serializers

from domain.school_operations.models import School
from domain.geography.models import Locality


class SchoolSerializer(serializers.ModelSerializer):
    """Serializer for School model."""
    
    locality_id = serializers.PrimaryKeyRelatedField(
        source='locality', queryset=Locality.objects.all()
    )
    
    class Meta:
        model = School
        fields = [
            "id",
            "name",
            "code",
            "locality_id",
            "address",
            "phone",
            "email",
            "website",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
        ]
        read_only_fields = [
            "id", "created_at", "updated_at", 
            "created_by", "updated_by", 
            "is_deleted", "deleted_at", "deleted_by"
        ]
