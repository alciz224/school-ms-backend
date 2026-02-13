"""Serializer for Cycle model."""
from rest_framework import serializers

from domain.academic.models import Cycle


class CycleSerializer(serializers.ModelSerializer):
    """Serializer for Cycle model."""

    tracks_count = serializers.SerializerMethodField()
    levels_count = serializers.SerializerMethodField()

    class Meta:
        model = Cycle
        fields = [
            "id",
            "code",
            "name",
            "has_track",
            "tracks_count",
            "levels_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_tracks_count(self, obj) -> int:
        """Get the number of tracks for this cycle."""
        return obj.tracks.count()

    def get_levels_count(self, obj) -> int:
        """Get the number of levels for this cycle."""
        return obj.levels.count()
