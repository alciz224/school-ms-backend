"""ViewSet for Level."""
from rest_framework import viewsets

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import LevelSerializer
from domain.academic.selectors import LevelSelector


class LevelViewSet(viewsets.ModelViewSet):
    """ViewSet for Level model."""

    serializer_class = LevelSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["cycle", "track"]
    search_fields = ["code", "name"]
    ordering_fields = ["order", "code", "name", "created_at"]
    ordering = ["cycle", "order"]
    
    def get_queryset(self):
        """Get queryset using selector."""
        return LevelSelector.get_all()
