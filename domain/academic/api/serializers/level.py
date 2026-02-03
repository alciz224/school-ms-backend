"""Serializer for Level model."""
from rest_framework import serializers

from domain.academic.models import Level


class LevelSerializer(serializers.ModelSerializer):
    """Serializer for Level model."""

    cycle_name = serializers.CharField(source="cycle.name", read_only=True)
    cycle_code = serializers.CharField(source="cycle.code", read_only=True)
    track_name = serializers.CharField(source="track.name", read_only=True)
    track_code = serializers.CharField(source="track.code", read_only=True)

    class Meta:
        model = Level
        fields = [
            "id",
            "code",
            "name",
            "cycle",
            "cycle_name",
            "cycle_code",
            "track",
            "track_name",
            "track_code",
            "order",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        """Validate the level data."""
        cycle = attrs.get("cycle")
        track = attrs.get("track")

        if cycle:
            # If cycle has tracks, track is required
            if cycle.has_track and not track:
                raise serializers.ValidationError(
                    {"track": f"Track is required for cycle '{cycle}'"}
                )

            # If cycle doesn't have tracks, track should be null
            if not cycle.has_track and track:
                raise serializers.ValidationError(
                    {"track": f"Cycle '{cycle}' does not support tracks"}
                )

        # Validate track belongs to the same cycle
        if track and cycle and track.cycle_id != cycle.id:
            raise serializers.ValidationError(
                {"track": "Track must belong to the same cycle"}
            )

        return attrs
