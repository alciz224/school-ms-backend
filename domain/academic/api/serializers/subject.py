"""Serializer for Subject model."""
from rest_framework import serializers

from domain.academic.models import Subject


class SubjectSerializer(serializers.ModelSerializer):
    """Serializer for Subject model."""

    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name",
            "description",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
