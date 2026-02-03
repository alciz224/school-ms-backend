"""ViewSet for AssessmentType."""
from rest_framework import viewsets

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import AssessmentTypeSerializer
from domain.academic.models import AssessmentType


class AssessmentTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for AssessmentType model."""

    queryset = AssessmentType.objects.all()
    serializer_class = AssessmentTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["name"]
