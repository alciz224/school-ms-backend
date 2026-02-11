from rest_framework import viewsets

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.enrollment.api.serializers import ClassroomSerializer
from domain.enrollment.models import Classroom
from domain.enrollment.selectors import ClassroomSelector


class ClassroomViewSet(viewsets.ModelViewSet):
    """
    CRUD for classrooms.
    
    Permissions: SCHOOL_ADMIN / STAFF only.
    """

    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = ClassroomSerializer

    def get_queryset(self):
        school_year_level_id = self.request.query_params.get("school_year_level")
        return ClassroomSelector.list(
            school_year_level_id=int(school_year_level_id) if school_year_level_id else None
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance: Classroom):
        instance.soft_delete(user=self.request.user)
