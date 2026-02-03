"""ViewSet for TermType."""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import TermTypeSerializer, TermSerializer
from domain.academic.models import TermType


class TermTypeViewSet(viewsets.ModelViewSet):
    """ViewSet for TermType model."""

    queryset = TermType.objects.all()
    serializer_class = TermTypeSerializer
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ["code", "name"]
    ordering_fields = ["period_count", "code", "name", "created_at"]
    ordering = ["period_count", "name"]

    @action(detail=True, methods=["get"])
    def terms(self, request, pk=None):
        """Get all terms for this term type."""
        term_type = self.get_object()
        terms = term_type.terms.all()
        serializer = TermSerializer(terms, many=True)
        return Response(serializer.data)
