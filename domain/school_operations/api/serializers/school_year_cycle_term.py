from rest_framework import serializers

from domain.school_operations.models import SchoolYearCycleTerm


class SchoolYearCycleTermSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYearCycleTerm
        fields = [
            "id",
            "school_year_cycle",
            "term",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
