"""Serializer for Track model."""
from rest_framework import serializers

from domain.academic.models import Track


class TrackSerializer(serializers.ModelSerializer):
    """Serializer for Track model."""

    cycle_name = serializers.CharField(source="cycle.name", read_only=True)
    cycle_code = serializers.CharField(source="cycle.code", read_only=True)
    levels_count = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            "id",
            "code",
            "name",
            "cycle",
            "cycle_name",
            "cycle_code",
            "levels_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_levels_count(self, obj) -> int:
        """Get the number of levels for this track."""
        return obj.levels.count()

    def validate(self, attrs):
        """Validate the track data."""
        cycle = attrs.get("cycle")

        if cycle and not cycle.has_track:
            raise serializers.ValidationError(
                {"cycle": f"Cycle '{cycle}' does not support tracks"}
            )

        return attrs
