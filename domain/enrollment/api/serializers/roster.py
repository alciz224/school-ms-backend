"""Serializers for roster / list views (portal-oriented)."""

from rest_framework import serializers

from domain.enrollment.models import Classroom, StudentEnrollment


class StudentEnrollmentRosterSerializer(serializers.ModelSerializer):
    """Lightweight serializer for roster lists (class lists, etc.)."""

    display_name = serializers.CharField(read_only=True)
    student_email = serializers.EmailField(source="student.email", read_only=True, allow_null=True)

    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "display_name",
            "first_name",
            "last_name",
            "classroom_suffix",
            "student",
            "student_email",
            "enrollment_status",
            "annual_identifier",
            "classroom_identifier",
        ]
        read_only_fields = fields


class ClassroomRosterSerializer(serializers.ModelSerializer):
    """Classroom with basic stats for portal views."""

    student_count = serializers.IntegerField(read_only=True)
    capacity_remaining = serializers.IntegerField(read_only=True)

    class Meta:
        model = Classroom
        fields = [
            "id",
            "name",
            "capacity",
            "room_number",
            "student_count",
            "capacity_remaining",
            "school_year_level",
        ]
        read_only_fields = fields
