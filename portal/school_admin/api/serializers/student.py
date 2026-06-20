from rest_framework import serializers

from domain.enrollment.models import StudentEnrollment


class SchoolAdminStudentSerializer(serializers.ModelSerializer):
    """
    Serializer matching the frontend `Student` interface for the school-admin portal.
    """
    id = serializers.CharField(source="student.id", default=None)
    full_name = serializers.CharField(source="display_name")
    
    # Missing fields in backend, mock or return null to satisfy frontend contract
    gender = serializers.SerializerMethodField()
    date_of_birth = serializers.SerializerMethodField()
    photo_url = serializers.SerializerMethodField()
    birthplace_locality_id = serializers.SerializerMethodField()
    birthplace_locality_name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    
    academic_year = serializers.CharField(source="school_year_level.school_year_cycle.school_year.name", default="")
    cycle = serializers.CharField(source="school_year_level.school_year_cycle.cycle.name", default="")
    option = serializers.CharField(source="school_year_level.track.name", default="")
    level = serializers.CharField(source="school_year_level.level.name", default="")
    classroom_id = serializers.CharField(source="classroom.id", default=None)
    class_name = serializers.CharField(source="classroom.name", default="")
    
    previous_classroom_id = serializers.CharField(source="previous_classroom.id", default=None)
    previous_class_name = serializers.CharField(source="previous_classroom.name", default=None)
    
    parent_name = serializers.SerializerMethodField()
    parent_phone = serializers.SerializerMethodField()
    parent_email = serializers.SerializerMethodField()

    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "annual_identifier",
            "first_name",
            "last_name",
            "full_name",
            "gender",
            "date_of_birth",
            "photo_url",
            "birthplace_locality_id",
            "birthplace_locality_name",
            "address",
            "academic_year",
            "school_year_level_id",
            "cycle",
            "option",
            "level",
            "classroom_id",
            "class_name",
            "previous_classroom_id",
            "previous_class_name",
            "enrollment_status",
            "enrollment_date",
            "start_date",
            "end_date",
            "transfer_reason",
            "parent_name",
            "parent_phone",
            "parent_email",
        ]

    def get_gender(self, obj) -> str:
        return "M"

    def get_date_of_birth(self, obj) -> str:
        return "2010-01-01"

    def get_photo_url(self, obj):
        return None

    def get_birthplace_locality_id(self, obj):
        return None

    def get_birthplace_locality_name(self, obj):
        return None

    def get_address(self, obj):
        return None

    def get_parent_name(self, obj):
        if hasattr(obj, "parents_data") and obj.parents_data:
            return obj.parents_data[0].get("name")
        return None

    def get_parent_phone(self, obj):
        if hasattr(obj, "parents_data") and obj.parents_data:
            return obj.parents_data[0].get("phone")
        return None

    def get_parent_email(self, obj):
        if hasattr(obj, "parents_data") and obj.parents_data:
            return obj.parents_data[0].get("email")
        return None
