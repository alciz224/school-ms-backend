"""ViewSet for AcademicYear."""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.academic.api.permissions import IsAdminOrReadOnly
from domain.academic.api.serializers import AcademicYearSerializer
from domain.academic.services import AcademicYearService
from domain.academic.selectors import AcademicYearSelector


class AcademicYearViewSet(viewsets.ModelViewSet):
    """ViewSet for AcademicYear model."""

    serializer_class = AcademicYearSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ["status", "is_current", "start_year"]
    search_fields = ["code"]
    ordering_fields = ["start_year", "created_at"]
    ordering = ["-start_year"]
    
    def get_queryset(self):
        """Get queryset using selector."""
        return AcademicYearSelector.get_all()

    @action(detail=False, methods=["get"])
    def current(self, request):
        """Get the current academic year."""
        current_year = AcademicYearSelector.get_current()
        if current_year:
            serializer = self.get_serializer(current_year)
            return Response(serializer.data)
        return Response(
            {"detail": "No current academic year found"},
            status=status.HTTP_404_NOT_FOUND,
        )

    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        """Activate an academic year."""
        academic_year = self.get_object()
        try:
            academic_year = AcademicYearService.activate(
                academic_year=academic_year,
                user=request.user
            )
            serializer = self.get_serializer(academic_year)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def archive(self, request, pk=None):
        """Archive an academic year."""
        academic_year = self.get_object()
        try:
            academic_year = AcademicYearService.archive(
                academic_year=academic_year,
                user=request.user
            )
            serializer = self.get_serializer(academic_year)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(detail=True, methods=["post"])
    def set_current(self, request, pk=None):
        """Set this year as the current academic year."""
        academic_year = self.get_object()
        try:
            academic_year = AcademicYearService.set_current(
                academic_year=academic_year,
                user=request.user
            )
            serializer = self.get_serializer(academic_year)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {"detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
