from rest_framework import serializers

from domain.school_operations.models import SchoolYearCycleTimeSlot


class SchoolYearCycleTimeSlotSerializer(serializers.ModelSerializer):
    """Serializer for SchoolYearCycleTimeSlot model."""
    
    class Meta:
        model = SchoolYearCycleTimeSlot
        fields = [
            "id",
            "school_year_cycle",
            "name",
            "start_time",
            "end_time",
            "order",
            "status",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
