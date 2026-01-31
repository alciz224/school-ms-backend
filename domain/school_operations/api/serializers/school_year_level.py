"""SchoolYearLevel serializers."""
from rest_framework import serializers

from domain.academic.api.serializers.level import LevelSerializer
from domain.academic.api.serializers.track import TrackSerializer
from domain.school_operations.models.school_year_level import SchoolYearLevel
from domain.school_operations.selectors.school_year_level import SchoolYearLevelSelector
from domain.school_operations.services.school_year_level import SchoolYearLevelService


class SchoolYearLevelSerializer(serializers.ModelSerializer):
    """
    Serializer for SchoolYearLevel with nested related objects.
    
    Used for read operations with full details.
    """

    from domain.school_operations.api.serializers.school_year_cycle import (
        SchoolYearCycleListSerializer,
    )

    school_year_cycle = SchoolYearCycleListSerializer(read_only=True)
    level = LevelSerializer(read_only=True)
    track = TrackSerializer(read_only=True)

    class Meta:
        model = SchoolYearLevel
        fields = [
            "id",
            "school_year_cycle",
            "level",
            "track",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "created_by",
            "updated_by",
        ]


class SchoolYearLevelListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.
    
    Includes only essential nested data.
    """

    school_year_display = serializers.CharField(
        source="school_year_cycle.school_year.__str__", read_only=True
    )
    cycle_name = serializers.CharField(
        source="school_year_cycle.cycle.name", read_only=True
    )
    level_name = serializers.CharField(source="level.name", read_only=True)
    level_code = serializers.CharField(source="level.code", read_only=True)
    level_order = serializers.IntegerField(source="level.order", read_only=True)
    track_name = serializers.CharField(source="track.name", read_only=True, allow_null=True)
    track_code = serializers.CharField(source="track.code", read_only=True, allow_null=True)

    class Meta:
        model = SchoolYearLevel
        fields = [
            "id",
            "school_year_display",
            "cycle_name",
            "level_name",
            "level_code",
            "level_order",
            "track_name",
            "track_code",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SchoolYearLevelCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a SchoolYearLevel.
    
    Uses service layer for creation with validation.
    """

    school_year_cycle_id = serializers.IntegerField()
    level_id = serializers.IntegerField()
    track_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_school_year_cycle_id(self, value):
        """Validate school_year_cycle_id exists."""
        from domain.school_operations.selectors.school_year_cycle import (
            SchoolYearCycleSelector,
        )

        school_year_cycle = SchoolYearCycleSelector.get_by_id(id=value)
        if not school_year_cycle:
            raise serializers.ValidationError("School year cycle does not exist")
        return value

    def validate_level_id(self, value):
        """Validate level_id exists."""
        from domain.academic.selectors.level import LevelSelector

        level = LevelSelector.get_by_id(id=value)
        if not level:
            raise serializers.ValidationError("Level does not exist")
        return value

    def validate_track_id(self, value):
        """Validate track_id exists if provided."""
        if value is not None:
            from domain.academic.selectors.track import TrackSelector

            track = TrackSelector.get_by_id(id=value)
            if not track:
                raise serializers.ValidationError("Track does not exist")
        return value

    def validate(self, attrs):
        """Validate uniqueness and business rules."""
        school_year_cycle_id = attrs.get("school_year_cycle_id")
        level_id = attrs.get("level_id")
        track_id = attrs.get("track_id")

        # Check uniqueness
        if SchoolYearLevelSelector.exists(
            school_year_cycle_id=school_year_cycle_id,
            level_id=level_id,
            track_id=track_id,
        ):
            raise serializers.ValidationError(
                "This level configuration already exists for this school year cycle"
            )

        return attrs

    def create(self, validated_data):
        """Create a new SchoolYearLevel using the service."""
        user = self.context.get("request").user if self.context.get("request") else None

        return SchoolYearLevelService.create(
            school_year_cycle_id=validated_data["school_year_cycle_id"],
            level_id=validated_data["level_id"],
            track_id=validated_data.get("track_id"),
            created_by=user if user and user.is_authenticated else None,
        )


class SchoolYearLevelUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating a SchoolYearLevel.
    
    Only track can be updated (school_year_cycle and level are immutable).
    """

    track_id = serializers.IntegerField(required=False, allow_null=True)

    def validate_track_id(self, value):
        """Validate track_id exists if provided."""
        if value is not None:
            from domain.academic.selectors.track import TrackSelector

            track = TrackSelector.get_by_id(id=value)
            if not track:
                raise serializers.ValidationError("Track does not exist")
        return value

    def update(self, instance, validated_data):
        """Update the SchoolYearLevel using the service."""
        user = self.context.get("request").user if self.context.get("request") else None

        return SchoolYearLevelService.update(
            school_year_level=instance,
            track_id=validated_data.get("track_id"),
            updated_by=user if user and user.is_authenticated else None,
        )


class SchoolYearLevelBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating level configurations for a school year cycle.
    
    Example:
        {
            "school_year_cycle_id": 1,
            "level_configs": [
                {"level_id": 1, "track_id": null},
                {"level_id": 2, "track_id": null}
            ]
        }
    """

    school_year_cycle_id = serializers.IntegerField()
    level_configs = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
    )

    def validate_school_year_cycle_id(self, value):
        """Validate school_year_cycle_id exists."""
        from domain.school_operations.selectors.school_year_cycle import (
            SchoolYearCycleSelector,
        )

        school_year_cycle = SchoolYearCycleSelector.get_by_id(id=value)
        if not school_year_cycle:
            raise serializers.ValidationError("School year cycle does not exist")
        return value

    def validate_level_configs(self, value):
        """Validate level_configs structure and uniqueness."""
        from domain.academic.selectors.level import LevelSelector
        from domain.academic.selectors.track import TrackSelector

        level_track_pairs = []
        for config in value:
            if "level_id" not in config:
                raise serializers.ValidationError("Each config must have 'level_id'")

            level_id = config["level_id"]
            track_id = config.get("track_id")

            # Check duplicates in the request
            pair = (level_id, track_id)
            if pair in level_track_pairs:
                raise serializers.ValidationError(
                    f"Duplicate level_id {level_id} with track_id {track_id} in configs"
                )
            level_track_pairs.append(pair)

            # Validate level exists
            if not LevelSelector.get_by_id(id=level_id):
                raise serializers.ValidationError(
                    f"Level with id {level_id} does not exist"
                )

            # Validate track exists if provided
            if track_id is not None and not TrackSelector.get_by_id(id=track_id):
                raise serializers.ValidationError(
                    f"Track with id {track_id} does not exist"
                )

        return value

    def create(self, validated_data):
        """Bulk create SchoolYearLevels using the service."""
        user = self.context.get("request").user if self.context.get("request") else None

        return SchoolYearLevelService.bulk_create_for_cycle(
            school_year_cycle_id=validated_data["school_year_cycle_id"],
            level_configs=validated_data["level_configs"],
            created_by=user if user and user.is_authenticated else None,
        )
