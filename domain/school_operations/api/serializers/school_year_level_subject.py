from rest_framework import serializers

from domain.school_operations.models import SchoolYearLevelSubject


class SchoolYearLevelSubjectSerializer(serializers.ModelSerializer):
    # Raw foreign-key ids required by the frontend to map existing data
    school_year_level_id = serializers.IntegerField(read_only=True)
    subject_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = SchoolYearLevelSubject
        fields = [
            "id",
            "school_year_level",
            "school_year_level_id",
            "subject",
            "subject_id",
            "coefficient",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]
