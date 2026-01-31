"""SchoolYearCycle serializers."""
from rest_framework import serializers

from domain.academic.api.serializers.cycle import CycleSerializer
from domain.academic.api.serializers.term_type import TermTypeSerializer
from domain.school_operations.models.school_year_cycle import SchoolYearCycle
from domain.school_operations.selectors.school_year_cycle import SchoolYearCycleSelector
from domain.school_operations.services.school_year_cycle import SchoolYearCycleService


class SchoolYearCycleSerializer(serializers.ModelSerializer):
    """
    Serializer for SchoolYearCycle with nested related objects.
    
    Used for read operations with full details.
    """

    from domain.school_operations.api.serializers.school_year import SchoolYearListSerializer
    
    school_year = SchoolYearListSerializer(read_only=True)
    cycle = CycleSerializer(read_only=True)
    term_type = TermTypeSerializer(read_only=True)

    class Meta:
        model = SchoolYearCycle
        fields = [
            "id",
            "school_year",
            "cycle",
            "term_type",
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


class SchoolYearCycleListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views.
    
    Includes only essential nested data.
    """

    school_year_display = serializers.CharField(
        source="school_year.__str__", read_only=True
    )
    cycle_name = serializers.CharField(source="cycle.name", read_only=True)
    cycle_code = serializers.CharField(source="cycle.code", read_only=True)
    term_type_name = serializers.CharField(source="term_type.name", read_only=True)
    term_type_period_count = serializers.IntegerField(
        source="term_type.period_count", read_only=True
    )

    class Meta:
        model = SchoolYearCycle
        fields = [
            "id",
            "school_year_display",
            "cycle_name",
            "cycle_code",
            "term_type_name",
            "term_type_period_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class SchoolYearCycleCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a SchoolYearCycle.
    
    Uses service layer for creation with validation.
    """

    school_year_id = serializers.IntegerField()
    cycle_id = serializers.IntegerField()
    term_type_id = serializers.IntegerField()

    def validate_school_year_id(self, value):
        """Validate school_year_id exists."""
        from domain.school_operations.selectors.school_year import SchoolYearSelector

        school_year = SchoolYearSelector.get_by_id(id=value)
        if not school_year:
            raise serializers.ValidationError("School year does not exist")
        return value

    def validate_cycle_id(self, value):
        """Validate cycle_id exists."""
        from domain.academic.selectors.cycle import CycleSelector

        cycle = CycleSelector.get_by_id(id=value)
        if not cycle:
            raise serializers.ValidationError("Cycle does not exist")
        return value

    def validate_term_type_id(self, value):
        """Validate term_type_id exists."""
        from domain.academic.selectors.term_type import TermTypeSelector

        term_type = TermTypeSelector.get_by_id(id=value)
        if not term_type:
            raise serializers.ValidationError("Term type does not exist")
        return value

    def validate(self, attrs):
        """Validate uniqueness of school_year and cycle combination."""
        school_year_id = attrs.get("school_year_id")
        cycle_id = attrs.get("cycle_id")

        if SchoolYearCycleSelector.exists(
            school_year_id=school_year_id, cycle_id=cycle_id
        ):
            raise serializers.ValidationError(
                "This cycle is already configured for this school year"
            )

        return attrs

    def create(self, validated_data):
        """Create a new SchoolYearCycle using the service."""
        user = self.context.get("request").user if self.context.get("request") else None

        return SchoolYearCycleService.create(
            school_year_id=validated_data["school_year_id"],
            cycle_id=validated_data["cycle_id"],
            term_type_id=validated_data["term_type_id"],
            created_by=user if user and user.is_authenticated else None,
        )


class SchoolYearCycleUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating a SchoolYearCycle.
    
    Only term_type can be updated (school_year and cycle are immutable).
    """

    term_type_id = serializers.IntegerField(required=False)

    def validate_term_type_id(self, value):
        """Validate term_type_id exists."""
        from domain.academic.selectors.term_type import TermTypeSelector

        term_type = TermTypeSelector.get_by_id(id=value)
        if not term_type:
            raise serializers.ValidationError("Term type does not exist")
        return value

    def update(self, instance, validated_data):
        """Update the SchoolYearCycle using the service."""
        user = self.context.get("request").user if self.context.get("request") else None

        return SchoolYearCycleService.update(
            school_year_cycle=instance,
            term_type_id=validated_data.get("term_type_id"),
            updated_by=user if user and user.is_authenticated else None,
        )


class SchoolYearCycleBulkCreateSerializer(serializers.Serializer):
    """
    Serializer for bulk creating cycle configurations for a school year.
    
    Example:
        {
            "school_year_id": 1,
            "cycle_configs": [
                {"cycle_id": 1, "term_type_id": 1},
                {"cycle_id": 2, "term_type_id": 2}
            ]
        }
    """

    school_year_id = serializers.IntegerField()
    cycle_configs = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
    )

    def validate_school_year_id(self, value):
        """Validate school_year_id exists."""
        from domain.school_operations.selectors.school_year import SchoolYearSelector

        school_year = SchoolYearSelector.get_by_id(id=value)
        if not school_year:
            raise serializers.ValidationError("School year does not exist")
        return value

    def validate_cycle_configs(self, value):
        """Validate cycle_configs structure and uniqueness."""
        from domain.academic.selectors.cycle import CycleSelector
        from domain.academic.selectors.term_type import TermTypeSelector

        cycle_ids = []
        for config in value:
            if "cycle_id" not in config or "term_type_id" not in config:
                raise serializers.ValidationError(
                    "Each config must have 'cycle_id' and 'term_type_id'"
                )

            cycle_id = config["cycle_id"]
            term_type_id = config["term_type_id"]

            # Check duplicates in the request
            if cycle_id in cycle_ids:
                raise serializers.ValidationError(
                    f"Duplicate cycle_id {cycle_id} in configs"
                )
            cycle_ids.append(cycle_id)

            # Validate cycle exists
            if not CycleSelector.get_by_id(id=cycle_id):
                raise serializers.ValidationError(
                    f"Cycle with id {cycle_id} does not exist"
                )

            # Validate term_type exists
            if not TermTypeSelector.get_by_id(id=term_type_id):
                raise serializers.ValidationError(
                    f"Term type with id {term_type_id} does not exist"
                )

        return value

    def create(self, validated_data):
        """Bulk create SchoolYearCycles using the service."""
        user = self.context.get("request").user if self.context.get("request") else None

        return SchoolYearCycleService.bulk_create_for_school_year(
            school_year_id=validated_data["school_year_id"],
            cycle_configs=validated_data["cycle_configs"],
            created_by=user if user and user.is_authenticated else None,
        )
