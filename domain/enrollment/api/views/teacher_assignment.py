from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.enrollment.api.serializers.teacher_assignment import (
    TeacherAssignmentCreateSerializer,
    TeacherAssignmentEndSerializer,
    TeacherAssignmentReplaceSerializer,
    TeacherAssignmentSerializer,
)
from domain.enrollment.models import Classroom, TeacherAssignment
from domain.enrollment.selectors import TeacherAssignmentSelector
from domain.enrollment.services import TeacherAssignmentService
from domain.school_operations.models import SchoolYearLevelSubject, SchoolYearTeacher


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    """
    CRUD for teacher assignments.
    
    Permissions: SCHOOL_ADMIN / STAFF only.
    
    Special actions:
    - POST /teacher-assignments/{id}/end/ — end assignment
    - POST /teacher-assignments/{id}/replace/ — replace teacher
    """

    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = TeacherAssignmentSerializer

    def get_queryset(self):
        classroom_id = self.request.query_params.get("classroom")
        teacher_id = self.request.query_params.get("teacher")
        status_filter = self.request.query_params.get("status")

        return TeacherAssignmentSelector.list(
            classroom_id=int(classroom_id) if classroom_id else None,
            school_year_teacher_id=int(teacher_id) if teacher_id else None,
            status=status_filter,
        )

    def create(self, request, *args, **kwargs):
        """Create a new teacher assignment."""
        input_serializer = TeacherAssignmentCreateSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        # Get related objects
        school_year_teacher = SchoolYearTeacher.objects.get(
            id=input_serializer.validated_data["school_year_teacher"]
        )
        classroom = Classroom.objects.get(id=input_serializer.validated_data["classroom"])
        school_year_level_subject = SchoolYearLevelSubject.objects.get(
            id=input_serializer.validated_data["school_year_level_subject"]
        )

        assignment = TeacherAssignmentService.create(
            school_year_teacher=school_year_teacher,
            classroom=classroom,
            school_year_level_subject=school_year_level_subject,
            start_date=input_serializer.validated_data["start_date"],
            user=request.user,
        )

        output_serializer = TeacherAssignmentSerializer(assignment)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """Limited update (only start_date for ACTIVE assignments)."""
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        # Only allow start_date updates
        allowed_fields = {"start_date"}
        update_data = {k: v for k, v in request.data.items() if k in allowed_fields}

        assignment = TeacherAssignmentService.update(
            obj=instance, 
            **update_data,
            user=request.user
        )

        output_serializer = TeacherAssignmentSerializer(assignment)
        return Response(output_serializer.data)

    def perform_destroy(self, instance):
        """Soft delete assignment."""
        TeacherAssignmentService.delete(obj=instance, user=self.request.user)

    @action(detail=True, methods=["post"], url_path="end")
    def end_assignment(self, request, pk=None):
        """End a teacher assignment."""
        assignment = self.get_object()
        input_serializer = TeacherAssignmentEndSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        ended_assignment = TeacherAssignmentService.end(
            obj=assignment,
            end_date=input_serializer.validated_data["end_date"],
            user=request.user,
        )

        output_serializer = TeacherAssignmentSerializer(ended_assignment)
        return Response(output_serializer.data)

    @action(detail=True, methods=["post"], url_path="replace")
    def replace_teacher(self, request, pk=None):
        """Replace a teacher assignment."""
        assignment = self.get_object()
        input_serializer = TeacherAssignmentReplaceSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        new_school_year_teacher = SchoolYearTeacher.objects.get(
            id=input_serializer.validated_data["new_school_year_teacher"]
        )

        new_assignment = TeacherAssignmentService.replace(
            obj=assignment,
            new_school_year_teacher=new_school_year_teacher,
            start_date=input_serializer.validated_data["start_date"],
            user=request.user,
        )

        output_serializer = TeacherAssignmentSerializer(new_assignment)
        return Response(output_serializer.data)