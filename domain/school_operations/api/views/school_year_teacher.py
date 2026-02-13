from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from domain.school_operations.api.serializers.school_year_teacher import (
    SchoolYearTeacherSerializer,
)
from domain.school_operations.selectors import SchoolYearTeacherSelector


class SchoolYearTeacherViewSet(viewsets.ModelViewSet):
    """
    CRUD for school year teachers.
    
    Manages teacher assignments to school years.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SchoolYearTeacherSerializer

    def get_queryset(self):
        school_year_id = self.request.query_params.get("school_year")
        teacher_id = self.request.query_params.get("teacher")
        status = self.request.query_params.get("status")
        return SchoolYearTeacherSelector.list(
            school_year_id=int(school_year_id) if school_year_id else None,
            teacher_id=int(teacher_id) if teacher_id else None,
            status=status,
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
