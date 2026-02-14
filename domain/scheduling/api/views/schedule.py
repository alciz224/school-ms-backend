"""Schedule API views."""

from datetime import date

from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.scheduling.api.permissions import (
    IsSchoolStaffOrAdmin,
    IsTeacher,
    IsStudent,
    IsParent,
)
from domain.scheduling.api.serializers import (
    ScheduleSerializer,
    ScheduleDetailSerializer,
    ScheduleCreateSerializer,
    ScheduleUpdateSerializer,
    TimetableSerializer,
    BulkScheduleCreateSerializer,
    ConflictCheckSerializer,
)
from domain.scheduling.constants import DayOfWeek
from domain.scheduling.models import Schedule
from domain.scheduling.selectors import ScheduleSelector
from domain.scheduling.services import ScheduleService, ScheduleConflictError


@extend_schema_view(
    list=extend_schema(summary="List schedules", tags=["Scheduling"]),
    retrieve=extend_schema(summary="Get schedule details", tags=["Scheduling"]),
    create=extend_schema(summary="Create schedule", tags=["Scheduling"]),
    update=extend_schema(summary="Update schedule", tags=["Scheduling"]),
    partial_update=extend_schema(summary="Partially update schedule", tags=["Scheduling"]),
    destroy=extend_schema(summary="Delete schedule", tags=["Scheduling"]),
)
class ScheduleViewSet(viewsets.ModelViewSet):
    """
    CRUD operations for schedules.
    
    Permissions: SCHOOL_ADMIN, STAFF
    """
    
    permission_classes = [IsSchoolStaffOrAdmin]
    
    def get_queryset(self):
        """Get queryset with filters."""
        school_year_id = self.request.query_params.get('school_year_id')
        school_year_cycle_id = self.request.query_params.get('school_year_cycle_id')
        status = self.request.query_params.get('status')
        
        return ScheduleSelector.get_all(
            school_year_id=school_year_id,
            school_year_cycle_id=school_year_cycle_id,
            status=status,
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer."""
        if self.action == 'retrieve':
            return ScheduleDetailSerializer
        elif self.action == 'create':
            return ScheduleCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ScheduleUpdateSerializer
        return ScheduleSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new schedule."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            schedule = ScheduleService.create(data=serializer.validated_data)
            output_serializer = ScheduleDetailSerializer(schedule)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        except ScheduleConflictError as e:
            return Response(
                {"error": str(e), "conflict": True},
                status=status.HTTP_409_CONFLICT
            )
    
    def update(self, request, *args, **kwargs):
        """Update a schedule."""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            schedule = ScheduleService.update(
                schedule_id=instance.id,
                data=serializer.validated_data
            )
            output_serializer = ScheduleDetailSerializer(schedule)
            return Response(output_serializer.data)
        except ScheduleConflictError as e:
            return Response(
                {"error": str(e), "conflict": True},
                status=status.HTTP_409_CONFLICT
            )
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a schedule."""
        instance = self.get_object()
        ScheduleService.delete(schedule_id=instance.id)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @extend_schema(
        summary="Change schedule status",
        tags=["Scheduling"],
        request={"new_status": str},
    )
    @action(detail=True, methods=['post'])
    def change_status(self, request, pk=None):
        """Change schedule status."""
        schedule = self.get_object()
        new_status = request.data.get('new_status')
        
        if not new_status:
            return Response(
                {"error": "new_status is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            updated_schedule = ScheduleService.change_status(
                schedule_id=schedule.id,
                new_status=new_status
            )
            serializer = ScheduleDetailSerializer(updated_schedule)
            return Response(serializer.data)
        except ScheduleConflictError as e:
            return Response(
                {"error": str(e), "conflict": True},
                status=status.HTTP_409_CONFLICT
            )


@extend_schema(tags=["Scheduling"])
class ScheduleConflictCheckView(APIView):
    """
    Check for scheduling conflicts before creating.
    
    Permissions: SCHOOL_ADMIN, STAFF
    """
    
    permission_classes = [IsSchoolStaffOrAdmin]
    
    @extend_schema(
        summary="Check for scheduling conflicts",
        request=ConflictCheckSerializer,
    )
    def post(self, request):
        """Check for conflicts."""
        serializer = ConflictCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        conflicts = ScheduleService.detect_conflicts(**serializer.validated_data)
        
        # Format conflicts for response
        response_data = {
            "has_conflicts": conflicts['has_conflicts'],
            "classroom_conflicts": [
                {
                    "id": s.id,
                    "classroom": s.classroom.name,
                    "subject": s.subject.name,
                    "teacher": f"{s.teacher.first_name} {s.teacher.last_name}",
                    "time": f"{s.time_slot.start_time}-{s.time_slot.end_time}",
                }
                for s in conflicts['classroom_conflicts']
            ],
            "teacher_conflicts": [
                {
                    "id": s.id,
                    "classroom": s.classroom.name,
                    "subject": s.subject.name,
                    "teacher": f"{s.teacher.first_name} {s.teacher.last_name}",
                    "time": f"{s.time_slot.start_time}-{s.time_slot.end_time}",
                }
                for s in conflicts['teacher_conflicts']
            ],
        }
        
        return Response(response_data)


@extend_schema(tags=["Scheduling"])
class ClassroomTimetableView(APIView):
    """
    Get timetable for a classroom.
    
    Permissions: SCHOOL_ADMIN, STAFF, TEACHER
    """
    
    permission_classes = [IsSchoolStaffOrAdmin | IsTeacher]
    
    @extend_schema(
        summary="Get classroom timetable",
        parameters=[
            {"name": "effective_date", "type": "string", "format": "date", "required": False},
        ],
    )
    def get(self, request, classroom_id):
        """Get classroom timetable."""
        effective_date_str = request.query_params.get('effective_date')
        effective_date = date.fromisoformat(effective_date_str) if effective_date_str else date.today()
        
        schedules = ScheduleSelector.get_by_classroom(
            classroom_id=classroom_id,
            effective_date=effective_date,
        )
        
        # Group by day
        timetable = {}
        for schedule in schedules:
            day = schedule.day_of_week
            if day not in timetable:
                timetable[day] = []
            
            timetable[day].append({
                'schedule_id': schedule.id,
                'time_slot': {
                    'id': schedule.time_slot.id,
                    'name': schedule.time_slot.name,
                    'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                    'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                    'order': schedule.time_slot.order,
                },
                'subject': schedule.subject.name,
                'teacher': f"{schedule.teacher.first_name} {schedule.teacher.last_name}",
            })
        
        # Format response
        formatted = [
            {
                'day_of_week': day,
                'day_of_week_display': dict(DayOfWeek.choices)[day],
                'sessions': sessions,
            }
            for day, sessions in sorted(timetable.items(), key=lambda x: list(DayOfWeek.values).index(x[0]))
        ]
        
        return Response(formatted)


@extend_schema(tags=["Scheduling"])
class TeacherScheduleView(APIView):
    """
    Get schedule for a teacher.
    
    Permissions: SCHOOL_ADMIN, STAFF, TEACHER (own schedule)
    """
    
    permission_classes = [IsSchoolStaffOrAdmin | IsTeacher]
    
    @extend_schema(
        summary="Get teacher schedule",
        parameters=[
            {"name": "effective_date", "type": "string", "format": "date", "required": False},
        ],
    )
    def get(self, request, teacher_id):
        """Get teacher schedule."""
        # Check permissions
        if request.user.role == 'TEACHER' and request.user.id != teacher_id:
            return Response(
                {"error": "You can only view your own schedule"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        effective_date_str = request.query_params.get('effective_date')
        effective_date = date.fromisoformat(effective_date_str) if effective_date_str else date.today()
        
        schedules = ScheduleSelector.get_by_teacher(
            teacher_id=teacher_id,
            effective_date=effective_date,
        )
        
        # Group by day
        timetable = {}
        for schedule in schedules:
            day = schedule.day_of_week
            if day not in timetable:
                timetable[day] = []
            
            timetable[day].append({
                'schedule_id': schedule.id,
                'time_slot': {
                    'id': schedule.time_slot.id,
                    'name': schedule.time_slot.name,
                    'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                    'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                    'order': schedule.time_slot.order,
                },
                'subject': schedule.subject.name,
                'classroom': schedule.classroom.name,
            })
        
        # Format response
        formatted = [
            {
                'day_of_week': day,
                'day_of_week_display': dict(DayOfWeek.choices)[day],
                'sessions': sessions,
            }
            for day, sessions in sorted(timetable.items(), key=lambda x: list(DayOfWeek.values).index(x[0]))
        ]
        
        return Response(formatted)


@extend_schema(tags=["Scheduling"])
class StudentTimetableView(APIView):
    """
    Get timetable for a student.
    
    Permissions: SCHOOL_ADMIN, STAFF, STUDENT (own), PARENT (child)
    """
    
    permission_classes = [IsSchoolStaffOrAdmin | IsStudent | IsParent]
    
    @extend_schema(
        summary="Get student timetable",
        parameters=[
            {"name": "effective_date", "type": "string", "format": "date", "required": False},
        ],
    )
    def get(self, request, student_id):
        """Get student timetable."""
        # Check permissions
        if request.user.role == 'STUDENT' and request.user.id != student_id:
            return Response(
                {"error": "You can only view your own timetable"},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # TODO: Add parent-child relationship check for PARENT role
        
        effective_date_str = request.query_params.get('effective_date')
        effective_date = date.fromisoformat(effective_date_str) if effective_date_str else date.today()
        
        schedules = ScheduleSelector.get_by_student(
            student_id=student_id,
            effective_date=effective_date,
        )
        
        # Group by day
        timetable = {}
        for schedule in schedules:
            day = schedule.day_of_week
            if day not in timetable:
                timetable[day] = []
            
            timetable[day].append({
                'schedule_id': schedule.id,
                'time_slot': {
                    'id': schedule.time_slot.id,
                    'name': schedule.time_slot.name,
                    'start_time': schedule.time_slot.start_time.strftime('%H:%M'),
                    'end_time': schedule.time_slot.end_time.strftime('%H:%M'),
                    'order': schedule.time_slot.order,
                },
                'subject': schedule.subject.name,
                'teacher': f"{schedule.teacher.first_name} {schedule.teacher.last_name}",
            })
        
        # Format response
        formatted = [
            {
                'day_of_week': day,
                'day_of_week_display': dict(DayOfWeek.choices)[day],
                'sessions': sessions,
            }
            for day, sessions in sorted(timetable.items(), key=lambda x: list(DayOfWeek.values).index(x[0]))
        ]
        
        return Response(formatted)


@extend_schema(tags=["Scheduling"])
class BulkScheduleCreateView(APIView):
    """
    Create multiple schedules at once.
    
    Permissions: SCHOOL_ADMIN, STAFF
    """
    
    permission_classes = [IsSchoolStaffOrAdmin]
    
    @extend_schema(
        summary="Bulk create schedules",
        request=BulkScheduleCreateSerializer,
    )
    def post(self, request):
        """Create multiple schedules."""
        serializer = BulkScheduleCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        schedules_data = [
            s.validated_data for s in serializer.validated_data['schedules']
        ]
        
        result = ScheduleService.bulk_create(schedules_data=schedules_data)
        
        return Response({
            "created_count": len(result['created']),
            "failed_count": len(result['failed']),
            "created": [ScheduleSerializer(s).data for s in result['created']],
            "failed": result['failed'],
        })
