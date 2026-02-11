from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from domain.school_operations.api.serializers.school_year_level_subject import (
    SchoolYearLevelSubjectSerializer,
)
from domain.school_operations.selectors import SchoolYearLevelSubjectSelector


class SchoolYearLevelSubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for school year level subjects (subject + coefficient per level).
    
    Essential for Assessment domain.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SchoolYearLevelSubjectSerializer

    def get_queryset(self):
        school_year_level_id = self.request.query_params.get("school_year_level")
        return SchoolYearLevelSubjectSelector.list(
            school_year_level_id=int(school_year_level_id) if school_year_level_id else None
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
