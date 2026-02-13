"""Serializer for TermType model."""
from rest_framework import serializers

from domain.academic.models import TermType


class TermTypeSerializer(serializers.ModelSerializer):
    """Serializer for TermType model."""

    terms_count = serializers.SerializerMethodField()

    class Meta:
        model = TermType
        fields = [
            "id",
            "code",
            "name",
            "period_count",
            "terms_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_terms_count(self, obj) -> int:
        """Get the number of terms for this term type."""
        return obj.terms.count()

    def validate_period_count(self, value):
        """Validate period count is positive."""
        if value <= 0:
            raise serializers.ValidationError(
                "Period count must be greater than 0"
            )
        return value
