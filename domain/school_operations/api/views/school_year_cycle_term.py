from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from domain.school_operations.api.serializers.school_year_cycle_term import (
    SchoolYearCycleTermSerializer,
)
from domain.school_operations.selectors import SchoolYearCycleTermSelector


class SchoolYearCycleTermViewSet(viewsets.ModelViewSet):
    """
    CRUD for school year cycle terms (concrete periods with dates).
    
    Essential for Assessment domain.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SchoolYearCycleTermSerializer

    def get_queryset(self):
        school_year_cycle_id = self.request.query_params.get("school_year_cycle")
        return SchoolYearCycleTermSelector.list(
            school_year_cycle_id=int(school_year_cycle_id) if school_year_cycle_id else None
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
