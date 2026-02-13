from rest_framework import serializers

from domain.school_operations.models import SchoolYearTeacher


class SchoolYearTeacherSerializer(serializers.ModelSerializer):
    """Serializer for SchoolYearTeacher model."""
    
    can_receive_assignments = serializers.ReadOnlyField()
    
    class Meta:
        model = SchoolYearTeacher
        fields = [
            "id",
            "school_year",
            "teacher",
            "status",
            "hire_date",
            "end_date",
            "can_receive_assignments",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "can_receive_assignments", "created_at", "updated_at"]
