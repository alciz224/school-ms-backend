"""Serializer for AssessmentType model."""
from rest_framework import serializers

from domain.academic.models import AssessmentType


class AssessmentTypeSerializer(serializers.ModelSerializer):
    """Serializer for AssessmentType model."""

    class Meta:
        model = AssessmentType
        fields = [
            "id",
            "code",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
