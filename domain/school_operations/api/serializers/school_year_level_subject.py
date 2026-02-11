from rest_framework import serializers

from domain.school_operations.models import SchoolYearLevelSubject


class SchoolYearLevelSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = SchoolYearLevelSubject
        fields = [
            "id",
            "school_year_level",
            "subject",
            "coefficient",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
