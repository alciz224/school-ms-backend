"""ViewSet for Track."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import TrackSerializer, LevelSerializer
from domain.academic.models import Track


class TrackViewSet(viewsets.ModelViewSet):
    """ViewSet for Track model."""

    queryset = Track.objects.all()
    serializer_class = TrackSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["cycle"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["cycle", "code"]

    @action(detail=True, methods=["get"])
    def levels(self, request, pk=None):
        """Get all levels for this track."""
        track = self.get_object()
        levels = track.levels.all()
        serializer = LevelSerializer(levels, many=True)
        return Response(serializer.data)
