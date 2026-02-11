from rest_framework import serializers

from domain.enrollment.models import StudentEnrollment


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField(read_only=True)
    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "student",
            "first_name",
            "last_name",
            "school_year_level",
            "classroom",
            "previous_classroom",
            "enrollment_status",
            "enrollment_date",
            "start_date",
            "end_date",
            "transfer_reason",
            "annual_identifier",
            "classroom_identifier",
            "classroom_suffix",
            "display_name",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "previous_classroom",
            "classroom_suffix",
            "created_at",
            "updated_at",
            "display_name",
        ]


class StudentEnrollmentTransferSerializer(serializers.Serializer):
    to_classroom = serializers.IntegerField()
    transfer_date = serializers.DateField(required=False)
    transfer_reason = serializers.CharField(required=False, allow_blank=True)
    classroom_identifier = serializers.CharField(required=False, allow_blank=True)
