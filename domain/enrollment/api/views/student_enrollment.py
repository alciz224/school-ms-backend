from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.enrollment.api.serializers import (
    StudentEnrollmentSerializer,
    StudentEnrollmentTransferSerializer,
)
from domain.enrollment.models import Classroom, StudentEnrollment
from domain.enrollment.selectors import StudentEnrollmentSelector
from domain.enrollment.services import StudentEnrollmentService


class StudentEnrollmentViewSet(viewsets.ModelViewSet):
    """
    CRUD for student enrollments.
    
    Permissions: SCHOOL_ADMIN / STAFF only.
    """

    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = StudentEnrollmentSerializer

    def get_queryset(self):
        school_year_level_id = self.request.query_params.get("school_year_level")
        classroom_id = self.request.query_params.get("classroom")
        return StudentEnrollmentSelector.list(
            school_year_level_id=int(school_year_level_id) if school_year_level_id else None,
            classroom_id=int(classroom_id) if classroom_id else None,
        )

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        enrollment = StudentEnrollmentService.create(**serializer.validated_data, user=request.user)
        out = self.get_serializer(enrollment)
        return Response(out.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        enrollment = StudentEnrollmentService.update(obj=instance, **serializer.validated_data, user=request.user)
        out = self.get_serializer(enrollment)
        return Response(out.data, status=status.HTTP_200_OK)

    def perform_destroy(self, instance: StudentEnrollment):
        instance.soft_delete(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="transfer")
    def transfer(self, request, pk=None):
        enrollment = self.get_object()
        input_serializer = StudentEnrollmentTransferSerializer(data=request.data)
        input_serializer.is_valid(raise_exception=True)

        to_classroom_id = input_serializer.validated_data["to_classroom"]
        to_classroom = Classroom.objects.get(id=to_classroom_id)

        enrollment = StudentEnrollmentService.transfer(
            obj=enrollment,
            to_classroom=to_classroom,
            transfer_date=input_serializer.validated_data.get("transfer_date"),
            transfer_reason=input_serializer.validated_data.get("transfer_reason"),
            classroom_identifier=input_serializer.validated_data.get("classroom_identifier"),
            user=request.user,
        )

        return Response(StudentEnrollmentSerializer(enrollment).data, status=status.HTTP_200_OK)
