"""ViewSet for Cycle."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import CycleSerializer, TrackSerializer, LevelSerializer
from domain.academic.selectors import CycleSelector, TrackSelector, LevelSelector


class CycleViewSet(viewsets.ModelViewSet):
    """ViewSet for Cycle model."""

    serializer_class = CycleSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["has_track"]
    search_fields = ["code", "name"]
    ordering_fields = ["code", "name", "created_at"]
    ordering = ["code"]
    
    def get_queryset(self):
        """Get queryset using selector."""
        return CycleSelector.get_all()

    @action(detail=True, methods=["get"])
    def tracks(self, request, pk=None):
        """Get all tracks for this cycle."""
        cycle = self.get_object()
        tracks = TrackSelector.for_cycle(cycle=cycle)
        serializer = TrackSerializer(tracks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=["get"])
    def levels(self, request, pk=None):
        """Get all levels for this cycle."""
        cycle = self.get_object()
        levels = LevelSelector.for_cycle(cycle=cycle)
        serializer = LevelSerializer(levels, many=True)
        return Response(serializer.data)
