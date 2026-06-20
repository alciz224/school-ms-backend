from rest_framework import serializers

from domain.account.models import TeacherProfile
from domain.school_operations.models import SchoolYearTeacher
from domain.enrollment.models import TeacherAssignment


class TeacherSerializer(serializers.ModelSerializer):
    """
    Serializer matching the frontend `Teacher` interface for the portal.

    Wraps TeacherProfile and exposes the underlying user identity fields
    so the frontend contract stays unchanged.
    """
    id = serializers.CharField()
    first_name = serializers.CharField(source="user.first_name")
    last_name = serializers.CharField(source="user.last_name")
    email = serializers.EmailField(source="user.email")
    phone = serializers.CharField(source="user.phone", allow_null=True, required=False)

    class Meta:
        model = TeacherProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
        ]


class SchoolYearTeacherSerializer(serializers.ModelSerializer):
    """
    Serializer matching frontend `SchoolYearTeacher` interface.
    """
    id = serializers.CharField(read_only=True)
    school_year_id = serializers.CharField()
    teacher_id = serializers.CharField(source="teacher.id")
    status = serializers.CharField()
    hire_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
    teacher = TeacherSerializer(read_only=True)

    class Meta:
        model = SchoolYearTeacher
        fields = [
            "id",
            "school_year_id",
            "teacher_id",
            "status",
            "hire_date",
            "end_date",
            "teacher",
        ]


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer matching frontend `TeacherAssignment` interface.
    """
    id = serializers.CharField(read_only=True)
    school_year_teacher_id = serializers.CharField()
    classroom_id = serializers.CharField()
    school_year_level_subject_id = serializers.CharField()
    assignment_status = serializers.CharField()
    start_date = serializers.DateField(allow_null=True, required=False)
    end_date = serializers.DateField(allow_null=True, required=False)
    replaced_by_id = serializers.CharField(source="replaced_by.id", allow_null=True, required=False)
    
    # Related data for display
    classroom_name = serializers.CharField(source="classroom.name", read_only=True, default="")
    subject_name = serializers.CharField(source="school_year_level_subject.subject.name", read_only=True, default="")
    level_name = serializers.CharField(source="school_year_level_subject.school_year_level.level.name", read_only=True, default="")
    track_name = serializers.CharField(source="school_year_level_subject.school_year_level.track.name", read_only=True, default="")

    class Meta:
        model = TeacherAssignment
        fields = [
            "id",
            "school_year_teacher_id",
            "classroom_id",
            "school_year_level_subject_id",
            "assignment_status",
            "start_date",
            "end_date",
            "replaced_by_id",
            "classroom_name",
            "subject_name",
            "level_name",
            "track_name",
        ]


class TeacherClassSerializer(serializers.Serializer):
    """
    Serializer matching frontend `TeacherClass` interface.
    """
    id = serializers.CharField()
    name = serializers.CharField()
    subject = serializers.CharField()
    level = serializers.CharField()
    students = serializers.IntegerField()
    color = serializers.CharField(default="blue")
    assignment_id = serializers.CharField()
