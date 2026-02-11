from rest_framework import serializers

from domain.enrollment.models import TeacherAssignment


class TeacherAssignmentSerializer(serializers.ModelSerializer):
    teacher_name = serializers.CharField(
        source="school_year_teacher.teacher.get_full_name", read_only=True
    )
    teacher_email = serializers.EmailField(
        source="school_year_teacher.teacher.email", read_only=True
    )
    classroom_name = serializers.CharField(source="classroom.name", read_only=True)
    subject_name = serializers.CharField(
        source="school_year_level_subject.subject.name", read_only=True
    )
    subject_coefficient = serializers.DecimalField(
        source="school_year_level_subject.coefficient", max_digits=5, decimal_places=2, read_only=True
    )

    class Meta:
        model = TeacherAssignment
        fields = [
            "id",
            "school_year_teacher",
            "classroom",
            "classroom_name",
            "school_year_level_subject",
            "assignment_status",
            "start_date",
            "end_date",
            "replaced_by",
            "teacher_name",
            "teacher_email", 
            "subject_name",
            "subject_coefficient",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "id",
            "assignment_status", 
            "end_date",
            "replaced_by",
            "teacher_name",
            "teacher_email",
            "classroom_name",
            "subject_name",
            "subject_coefficient",
            "created_at",
            "updated_at",
        ]


class TeacherAssignmentCreateSerializer(serializers.Serializer):
    """Dedicated serializer for creating teacher assignments."""
    
    school_year_teacher = serializers.IntegerField()
    classroom = serializers.IntegerField()
    school_year_level_subject = serializers.IntegerField()
    start_date = serializers.DateField()


class TeacherAssignmentReplaceSerializer(serializers.Serializer):
    """Serializer for replacing a teacher assignment."""
    
    new_school_year_teacher = serializers.IntegerField()
    start_date = serializers.DateField()


class TeacherAssignmentEndSerializer(serializers.Serializer):
    """Serializer for ending a teacher assignment."""
    
    end_date = serializers.DateField()


class TeacherClassroomListSerializer(serializers.Serializer):
    """Serializer for teacher's classroom list (portal view)."""
    
    id = serializers.IntegerField()
    name = serializers.CharField()
    school_year_level = serializers.DictField()
    subjects = serializers.ListField()