"""ViewSet for Term."""
from rest_framework import viewsets

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import TermSerializer
from domain.academic.models import Term


class TermViewSet(viewsets.ModelViewSet):
    """ViewSet for Term model."""

    queryset = Term.objects.all()
    serializer_class = TermSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["term_type"]
    search_fields = ["code", "name"]
    ordering_fields = ["order", "code", "created_at"]
    ordering = ["term_type", "order"]
