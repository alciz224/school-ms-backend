from rest_framework import serializers

from domain.school_operations.models import SchoolYearCycleTimeSlot
from domain.scheduling.models import Schedule
from domain.scheduling.constants import DayOfWeek, ScheduleStatus


class SchoolYearCycleTimeSlotSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    duration_minutes = serializers.SerializerMethodField()

    class Meta:
        model = SchoolYearCycleTimeSlot
        fields = [
            "id",
            "school_year_cycle_id",
            "name",
            "order",
            "start_time",
            "end_time",
            "duration_minutes",
            "status",
        ]

    def get_duration_minutes(self, obj):
        if obj.start_time and obj.end_time:
            start = obj.start_time.hour * 60 + obj.start_time.minute
            end = obj.end_time.hour * 60 + obj.end_time.minute
            return end - start
        return 0


class ScheduleSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    subject_color = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = [
            "id",
            "school_year_id",
            "school_year_cycle_id",
            "classroom_id",
            "teacher_assignment_id",
            "day_of_week",
            "time_slot_id",
            "effective_from",
            "effective_to",
            "status",
            "teacher_name",
            "subject_name",
            "subject_color",
        ]

    def get_teacher_name(self, obj):
        teacher = obj.teacher
        if teacher:
            return teacher.full_name
        return ""

    def get_subject_name(self, obj):
        try:
            return obj.subject.name
        except Exception:
            return ""

    def get_subject_color(self, obj):
        try:
            name = obj.subject.name.upper()
        except Exception:
            return "blue"
        color_map = {
            "MATHEMATIQUES": "blue", "FRANCAIS": "green", "PHYSIQUE": "red",
            "ANGLAIS": "yellow", "HISTOIRE": "purple", "GEOGRAPHIE": "orange",
            "SCIENCES": "teal", "PHILOSOPHIE": "indigo", "SPORT": "pink",
        }
        return color_map.get(name.split()[0], "blue")


class ScheduleCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = [
            "school_year",
            "school_year_cycle",
            "classroom",
            "teacher_assignment",
            "day_of_week",
            "time_slot",
            "effective_from",
            "effective_to",
            "status",
        ]


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = [
            "day_of_week",
            "time_slot",
            "effective_from",
            "effective_to",
            "status",
        ]
        extra_kwargs = {field: {"required": False} for field in fields}
