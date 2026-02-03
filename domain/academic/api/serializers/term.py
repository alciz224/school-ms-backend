"""Serializer for Term model."""
from rest_framework import serializers

from domain.academic.models import Term


class TermSerializer(serializers.ModelSerializer):
    """Serializer for Term model."""

    term_type_name = serializers.CharField(source="term_type.name", read_only=True)
    term_type_code = serializers.CharField(source="term_type.code", read_only=True)
    period_count = serializers.IntegerField(
        source="term_type.period_count", read_only=True
    )

    class Meta:
        model = Term
        fields = [
            "id",
            "term_type",
            "term_type_name",
            "term_type_code",
            "period_count",
            "code",
            "name",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """Validate the term data."""
        term_type = attrs.get("term_type")
        order = attrs.get("order")

        if term_type and order:
            if order <= 0:
                raise serializers.ValidationError(
                    {"order": "Order must be greater than 0"}
                )

            if order > term_type.period_count:
                raise serializers.ValidationError(
                    {
                        "order": f"Order cannot exceed {term_type.period_count} "
                        f"for term type '{term_type}'"
                    }
                )

        return attrs
