from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.school_operations.models import SchoolYearCycleTimeSlot
from domain.scheduling.models import Schedule
from domain.scheduling.selectors import ScheduleSelector
from domain.scheduling.constants import DayOfWeek

from portal.school_admin.api.serializers.schedule import (
    SchoolYearCycleTimeSlotSerializer,
    ScheduleSerializer,
    ScheduleCreateSerializer,
    ScheduleUpdateSerializer,
)

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class TimeSlotListView(APIView):
    """
    List time slots for a school year cycle.
    GET /school-year-cycles/{schoolYearCycleId}/time-slots/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolYearCycleTimeSlotSerializer(many=True))
    def get(self, request, school_year_cycle_id=None):
        qs = SchoolYearCycleTimeSlot.objects.filter(
            school_year_cycle_id=school_year_cycle_id, is_deleted=False
        ).order_by("order")
        serializer = SchoolYearCycleTimeSlotSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


class TimeSlotViewSet(viewsets.ModelViewSet):
    """
    CRUD for time slots.
    """
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = SchoolYearCycleTimeSlotSerializer
    lookup_field = "id"

    def get_queryset(self):
        return SchoolYearCycleTimeSlot.objects.filter(is_deleted=False)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)


class ClassroomScheduleView(APIView):
    """
    Get schedule for a classroom.
    GET /classrooms/{classroomId}/schedule/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("effective_date", OpenApiTypes.DATE, required=False),
        ],
        responses=ScheduleSerializer(many=True),
    )
    def get(self, request, classroom_id=None):
        from datetime import date
        effective_date_str = request.query_params.get("effective_date")
        effective_date = date.fromisoformat(effective_date_str) if effective_date_str else date.today()

        schedules = ScheduleSelector.get_by_classroom(
            classroom_id=classroom_id,
            effective_date=effective_date,
        )
        serializer = ScheduleSerializer(schedules, many=True)
        return Response({"success": True, "data": serializer.data})


class TeacherAssignmentScheduleView(APIView):
    """
    Get schedule for a teacher assignment.
    GET /teacher-assignments/{teacherAssignmentId}/schedule/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("effective_date", OpenApiTypes.DATE, required=False),
        ],
        responses=ScheduleSerializer(many=True),
    )
    def get(self, request, teacher_assignment_id=None):
        from datetime import date
        effective_date_str = request.query_params.get("effective_date")
        effective_date = date.fromisoformat(effective_date_str) if effective_date_str else date.today()

        schedules = Schedule.objects.filter(
            is_deleted=False,
            teacher_assignment_id=teacher_assignment_id,
            effective_from__lte=effective_date,
        ).filter(
            effective_to__isnull=True
        ) | Schedule.objects.filter(
            is_deleted=False,
            teacher_assignment_id=teacher_assignment_id,
            effective_from__lte=effective_date,
            effective_to__gte=effective_date,
        )
        serializer = ScheduleSerializer(schedules, many=True)
        return Response({"success": True, "data": serializer.data})


class ScheduleViewSet(viewsets.ModelViewSet):
    """
    CRUD for schedule blocks.
    """
    permission_classes = [IsSchoolStaffOrAdmin]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "create":
            return ScheduleCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return ScheduleUpdateSerializer
        return ScheduleSerializer

    def get_queryset(self):
        qs = Schedule.objects.filter(is_deleted=False).select_related(
            "teacher_assignment__school_year_teacher__teacher",
            "teacher_assignment__school_year_level_subject__subject",
            "classroom",
            "time_slot",
        )
        classroom_id = self.request.query_params.get("classroom_id")
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
