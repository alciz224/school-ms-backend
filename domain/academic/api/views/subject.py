"""ViewSet for Subject."""
from rest_framework import viewsets

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import SubjectSerializer
from domain.academic.models import Subject


class SubjectViewSet(viewsets.ModelViewSet):
    """ViewSet for Subject model."""

    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
