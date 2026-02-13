from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated

from domain.school_operations.api.serializers.school import SchoolSerializer
from domain.school_operations.selectors import SchoolSelector


class SchoolViewSet(viewsets.ModelViewSet):
    """
    CRUD for schools.
    
    Manages school information and settings.
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SchoolSerializer

    def get_queryset(self):
        locality_id = self.request.query_params.get("locality")
        status = self.request.query_params.get("status")
        return SchoolSelector.list(
            locality_id=int(locality_id) if locality_id else None,
            status=status,
        )

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)
