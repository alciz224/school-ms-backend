"""SchoolYearLevel API views."""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.school_operations.api.serializers.school_year_level import (
    SchoolYearLevelBulkCreateSerializer,
    SchoolYearLevelCreateSerializer,
    SchoolYearLevelListSerializer,
    SchoolYearLevelSerializer,
    SchoolYearLevelUpdateSerializer,
)
from domain.school_operations.selectors.school_year_level import SchoolYearLevelSelector
from domain.school_operations.services.school_year_level import SchoolYearLevelService
from domain.shared.api.pagination import StandardPagination


@extend_schema_view(
    list=extend_schema(
        summary="List all school year levels",
        description="Retrieve a paginated list of all school year level configurations.",
        tags=["School Operations - School Year Levels"],
    ),
    retrieve=extend_schema(
        summary="Get school year level details",
        description="Retrieve detailed information about a specific school year level.",
        tags=["School Operations - School Year Levels"],
    ),
    create=extend_schema(
        summary="Create a school year level",
        description="Create a new level configuration for a school year cycle.",
        tags=["School Operations - School Year Levels"],
    ),
    update=extend_schema(
        summary="Update a school year level",
        description="Update a school year level configuration (only track can be changed).",
        tags=["School Operations - School Year Levels"],
    ),
    partial_update=extend_schema(
        summary="Partially update a school year level",
        description="Partially update a school year level configuration.",
        tags=["School Operations - School Year Levels"],
    ),
    destroy=extend_schema(
        summary="Delete a school year level",
        description="Soft delete a school year level configuration.",
        tags=["School Operations - School Year Levels"],
    ),
)
class SchoolYearLevelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing school year level configurations.

    Provides CRUD operations for linking levels to school year cycles.
    """

    pagination_class = StandardPagination
    lookup_field = "id"

    def get_queryset(self):
        """Get queryset based on action."""
        queryset = SchoolYearLevelSelector.get_queryset()

        # Filter by query parameters
        school_year_cycle_id = self.request.query_params.get("school_year_cycle_id")
        school_year_id = self.request.query_params.get("school_year_id")
        school_id = self.request.query_params.get("school_id")
        cycle_id = self.request.query_params.get("cycle_id")
        level_id = self.request.query_params.get("level_id")
        track_id = self.request.query_params.get("track_id")
        academic_year_id = self.request.query_params.get("academic_year_id")
        search = self.request.query_params.get("search")

        if school_year_cycle_id:
            queryset = queryset.filter(school_year_cycle_id=school_year_cycle_id)

        if school_year_id:
            queryset = queryset.filter(school_year_cycle__school_year_id=school_year_id)

        if school_id:
            queryset = queryset.filter(
                school_year_cycle__school_year__school_id=school_id
            )

        if cycle_id:
            queryset = queryset.filter(school_year_cycle__cycle_id=cycle_id)

        if level_id:
            queryset = queryset.filter(level_id=level_id)

        if track_id:
            queryset = queryset.filter(track_id=track_id)

        if academic_year_id:
            queryset = queryset.filter(
                school_year_cycle__school_year__academic_year_id=academic_year_id
            )

        if search:
            queryset = SchoolYearLevelSelector.search(query=search)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return SchoolYearLevelListSerializer
        elif self.action == "create":
            return SchoolYearLevelCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return SchoolYearLevelUpdateSerializer
        elif self.action == "bulk_create":
            return SchoolYearLevelBulkCreateSerializer
        return SchoolYearLevelSerializer

    def perform_destroy(self, instance):
        """Soft delete the instance using the service."""
        user = self.request.user if self.request.user.is_authenticated else None
        SchoolYearLevelService.delete(
            school_year_level=instance,
            deleted_by=user,
        )

    @extend_schema(
        summary="Get levels by school year cycle",
        description="Retrieve all level configurations for a specific school year cycle.",
        tags=["School Operations - School Year Levels"],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="by-school-year-cycle/(?P<school_year_cycle_id>[^/.]+)",
    )
    def by_school_year_cycle(self, request, school_year_cycle_id=None):
        """Get all levels for a specific school year cycle."""
        levels = SchoolYearLevelSelector.list_by_school_year_cycle(
            school_year_cycle_id=int(school_year_cycle_id)
        )
        serializer = SchoolYearLevelListSerializer(levels, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get levels by school year",
        description="Retrieve all level configurations for a specific school year.",
        tags=["School Operations - School Year Levels"],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="by-school-year/(?P<school_year_id>[^/.]+)",
    )
    def by_school_year(self, request, school_year_id=None):
        """Get all levels for a specific school year."""
        levels = SchoolYearLevelSelector.list_by_school_year(
            school_year_id=int(school_year_id)
        )
        serializer = SchoolYearLevelListSerializer(levels, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get levels by school",
        description="Retrieve all level configurations for a specific school across all years.",
        tags=["School Operations - School Year Levels"],
    )
    @action(detail=False, methods=["get"], url_path="by-school/(?P<school_id>[^/.]+)")
    def by_school(self, request, school_id=None):
        """Get all levels for a specific school."""
        levels = SchoolYearLevelSelector.list_by_school(school_id=int(school_id))
        serializer = SchoolYearLevelListSerializer(levels, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get active levels",
        description="Retrieve all level configurations for currently active school years.",
        tags=["School Operations - School Year Levels"],
    )
    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get levels for active school years."""
        levels = SchoolYearLevelSelector.list_active_levels()
        serializer = SchoolYearLevelListSerializer(levels, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get active levels by school",
        description="Retrieve level configurations for a school's active school year.",
        tags=["School Operations - School Year Levels"],
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="active/by-school/(?P<school_id>[^/.]+)",
    )
    def active_by_school(self, request, school_id=None):
        """Get levels for a school's active school year."""
        levels = SchoolYearLevelSelector.list_by_school_and_active_year(
            school_id=int(school_id)
        )
        serializer = SchoolYearLevelListSerializer(levels, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Bulk create levels for school year cycle",
        description="Create multiple level configurations for a school year cycle at once.",
        tags=["School Operations - School Year Levels"],
        request=SchoolYearLevelBulkCreateSerializer,
        responses={201: SchoolYearLevelListSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Bulk create level configurations for a school year cycle."""
        serializer = SchoolYearLevelBulkCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        levels = serializer.save()

        response_serializer = SchoolYearLevelListSerializer(levels, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Restore a deleted level",
        description="Restore a soft-deleted school year level configuration.",
        tags=["School Operations - School Year Levels"],
    )
    @action(detail=True, methods=["post"])
    def restore(self, request, id=None):
        """Restore a soft-deleted level."""
        level = self.get_object()

        if not level.is_deleted:
            return Response(
                {"detail": "Level is not deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user if request.user.is_authenticated else None
        restored_level = SchoolYearLevelService.restore(
            school_year_level=level,
            updated_by=user,
        )

        serializer = SchoolYearLevelSerializer(restored_level)
        return Response(serializer.data)
