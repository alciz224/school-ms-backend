"""Schedule serializers."""

from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field, inline_serializer

from domain.scheduling.models import Schedule
from domain.scheduling.constants import DayOfWeek, ScheduleStatus


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for Schedule model (list view)."""
    
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    teacher_name = serializers.SerializerMethodField()
    subject_name = serializers.CharField(
        source='teacher_assignment.school_year_level_subject.subject.name',
        read_only=True
    )
    time_slot_display = serializers.SerializerMethodField()
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id',
            'school_year',
            'school_year_cycle',
            'classroom',
            'classroom_name',
            'teacher_assignment',
            'teacher_name',
            'subject_name',
            'day_of_week',
            'day_of_week_display',
            'time_slot',
            'time_slot_display',
            'effective_from',
            'effective_to',
            'status',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    @extend_schema_field(serializers.CharField())
    def get_teacher_name(self, obj) -> str:
        """Get teacher full name."""
        teacher = obj.teacher
        return f"{teacher.first_name} {teacher.last_name}"
    
    @extend_schema_field(serializers.CharField())
    def get_time_slot_display(self, obj) -> str:
        """Get time slot display string."""
        return f"{obj.time_slot.start_time.strftime('%H:%M')}-{obj.time_slot.end_time.strftime('%H:%M')}"


class ScheduleDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for Schedule model (detail view)."""
    
    classroom = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    subject = serializers.SerializerMethodField()
    time_slot_info = serializers.SerializerMethodField()
    day_of_week_display = serializers.CharField(source='get_day_of_week_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Schedule
        fields = [
            'id',
            'school_year',
            'school_year_cycle',
            'classroom',
            'teacher',
            'subject',
            'teacher_assignment',
            'day_of_week',
            'day_of_week_display',
            'time_slot',
            'time_slot_info',
            'effective_from',
            'effective_to',
            'status',
            'status_display',
            'is_active',
            'is_archived',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'is_active', 'is_archived', 'created_at', 'updated_at']
    
    @extend_schema_field(inline_serializer(
        name='ClassroomInfo',
        fields={
            'id': serializers.IntegerField(),
            'name': serializers.CharField(),
            'capacity': serializers.IntegerField(),
        }
    ))
    def get_classroom(self, obj):
        """Get classroom details."""
        return {
            'id': obj.classroom.id,
            'name': obj.classroom.name,
            'capacity': obj.classroom.capacity,
        }
    
    @extend_schema_field(inline_serializer(
        name='TeacherInfo',
        fields={
            'id': serializers.IntegerField(),
            'first_name': serializers.CharField(),
            'last_name': serializers.CharField(),
            'email': serializers.EmailField(),
        }
    ))
    def get_teacher(self, obj):
        """Get teacher details."""
        teacher = obj.teacher
        return {
            'id': teacher.id,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'email': teacher.email,
        }
    
    @extend_schema_field(inline_serializer(
        name='SubjectInfo',
        fields={
            'id': serializers.IntegerField(),
            'name': serializers.CharField(),
            'code': serializers.CharField(),
        }
    ))
    def get_subject(self, obj):
        """Get subject details."""
        subject = obj.subject
        return {
            'id': subject.id,
            'name': subject.name,
            'code': subject.code,
        }
    
    @extend_schema_field(inline_serializer(
        name='TimeSlotInfo',
        fields={
            'id': serializers.IntegerField(),
            'name': serializers.CharField(),
            'start_time': serializers.CharField(),
            'end_time': serializers.CharField(),
            'order': serializers.IntegerField(),
        }
    ))
    def get_time_slot_info(self, obj):
        """Get time slot details."""
        time_slot = obj.time_slot
        return {
            'id': time_slot.id,
            'name': time_slot.name,
            'start_time': time_slot.start_time.strftime('%H:%M'),
            'end_time': time_slot.end_time.strftime('%H:%M'),
            'order': time_slot.order,
        }


class ScheduleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating schedules."""
    
    class Meta:
        model = Schedule
        fields = [
            'school_year',
            'school_year_cycle',
            'classroom',
            'teacher_assignment',
            'day_of_week',
            'time_slot',
            'effective_from',
            'effective_to',
            'status',
        ]
    
    def validate(self, attrs):
        """Additional validation."""
        # Convert to dict with IDs for service layer
        return {
            'school_year_id': attrs['school_year'].id,
            'school_year_cycle_id': attrs['school_year_cycle'].id,
            'classroom_id': attrs['classroom'].id,
            'teacher_assignment_id': attrs['teacher_assignment'].id,
            'day_of_week': attrs['day_of_week'],
            'time_slot_id': attrs['time_slot'].id,
            'effective_from': attrs['effective_from'],
            'effective_to': attrs.get('effective_to'),
            'status': attrs.get('status', ScheduleStatus.DRAFT),
        }


class ScheduleUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating schedules."""
    
    class Meta:
        model = Schedule
        fields = [
            'day_of_week',
            'time_slot',
            'effective_from',
            'effective_to',
            'status',
        ]
        extra_kwargs = {
            'day_of_week': {'required': False},
            'time_slot': {'required': False},
            'effective_from': {'required': False},
            'effective_to': {'required': False},
            'status': {'required': False},
        }


class TimetableSerializer(serializers.Serializer):
    """Serializer for formatted timetable display."""
    
    day_of_week = serializers.ChoiceField(choices=DayOfWeek.choices)
    day_of_week_display = serializers.CharField()
    sessions = serializers.ListField(child=serializers.DictField())
    
    # Each session in sessions contains:
    # {
    #   'time_slot': {...},
    #   'subject': str,
    #   'teacher': str,
    #   'classroom': str (optional for teacher view),
    #   'schedule_id': int
    # }


class BulkScheduleCreateSerializer(serializers.Serializer):
    """Serializer for bulk schedule creation."""
    
    schedules = serializers.ListField(
        child=ScheduleCreateSerializer(),
        min_length=1,
    )


class ConflictCheckSerializer(serializers.Serializer):
    """Serializer for conflict checking."""
    
    classroom_id = serializers.IntegerField()
    teacher_assignment_id = serializers.IntegerField()
    day_of_week = serializers.ChoiceField(choices=DayOfWeek.choices)
    time_slot_id = serializers.IntegerField()
    effective_from = serializers.DateField()
    effective_to = serializers.DateField(required=False, allow_null=True)
