"""SchoolYearCycle API views."""
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from domain.school_operations.api.serializers.school_year_cycle import (
    SchoolYearCycleBulkCreateSerializer,
    SchoolYearCycleCreateSerializer,
    SchoolYearCycleListSerializer,
    SchoolYearCycleSerializer,
    SchoolYearCycleUpdateSerializer,
)
from domain.school_operations.models.school_year_cycle import SchoolYearCycle
from domain.school_operations.selectors.school_year_cycle import SchoolYearCycleSelector
from domain.school_operations.services.school_year_cycle import SchoolYearCycleService
from domain.shared.api.pagination import StandardPagination


@extend_schema_view(
    list=extend_schema(
        summary="List all school year cycles",
        description="Retrieve a paginated list of all school year cycle configurations.",
        tags=["School Operations - School Year Cycles"],
    ),
    retrieve=extend_schema(
        summary="Get school year cycle details",
        description="Retrieve detailed information about a specific school year cycle.",
        tags=["School Operations - School Year Cycles"],
    ),
    create=extend_schema(
        summary="Create a school year cycle",
        description="Create a new cycle configuration for a school year.",
        tags=["School Operations - School Year Cycles"],
    ),
    update=extend_schema(
        summary="Update a school year cycle",
        description="Update a school year cycle configuration (only term_type can be changed).",
        tags=["School Operations - School Year Cycles"],
    ),
    partial_update=extend_schema(
        summary="Partially update a school year cycle",
        description="Partially update a school year cycle configuration.",
        tags=["School Operations - School Year Cycles"],
    ),
    destroy=extend_schema(
        summary="Delete a school year cycle",
        description="Soft delete a school year cycle configuration.",
        tags=["School Operations - School Year Cycles"],
    ),
)
class SchoolYearCycleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing school year cycle configurations.

    Provides CRUD operations for linking cycles to school years with term types.
    """

    pagination_class = StandardPagination
    lookup_field = "id"

    def get_queryset(self):
        """Get queryset based on action."""
        queryset = SchoolYearCycleSelector.get_queryset()

        # Filter by query parameters
        school_year_id = self.request.query_params.get("school_year_id")
        school_id = self.request.query_params.get("school_id")
        cycle_id = self.request.query_params.get("cycle_id")
        term_type_id = self.request.query_params.get("term_type_id")
        academic_year_id = self.request.query_params.get("academic_year_id")
        search = self.request.query_params.get("search")

        if school_year_id:
            queryset = queryset.filter(school_year_id=school_year_id)

        if school_id:
            queryset = queryset.filter(school_year__school_id=school_id)

        if cycle_id:
            queryset = queryset.filter(cycle_id=cycle_id)

        if term_type_id:
            queryset = queryset.filter(term_type_id=term_type_id)

        if academic_year_id:
            queryset = queryset.filter(school_year__academic_year_id=academic_year_id)

        if search:
            queryset = SchoolYearCycleSelector.search(query=search)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == "list":
            return SchoolYearCycleListSerializer
        elif self.action == "create":
            return SchoolYearCycleCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return SchoolYearCycleUpdateSerializer
        elif self.action == "bulk_create":
            return SchoolYearCycleBulkCreateSerializer
        return SchoolYearCycleSerializer

    def perform_destroy(self, instance):
        """Soft delete the instance using the service."""
        user = self.request.user if self.request.user.is_authenticated else None
        SchoolYearCycleService.delete(
            school_year_cycle=instance,
            deleted_by=user,
        )

    @extend_schema(
        summary="Get cycles by school year",
        description="Retrieve all cycle configurations for a specific school year.",
        tags=["School Operations - School Year Cycles"],
    )
    @action(detail=False, methods=["get"], url_path="by-school-year/(?P<school_year_id>[^/.]+)")
    def by_school_year(self, request, school_year_id=None):
        """Get all cycles for a specific school year."""
        cycles = SchoolYearCycleSelector.list_by_school_year(
            school_year_id=int(school_year_id)
        )
        serializer = SchoolYearCycleListSerializer(cycles, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get cycles by school",
        description="Retrieve all cycle configurations for a specific school across all years.",
        tags=["School Operations - School Year Cycles"],
    )
    @action(detail=False, methods=["get"], url_path="by-school/(?P<school_id>[^/.]+)")
    def by_school(self, request, school_id=None):
        """Get all cycles for a specific school."""
        cycles = SchoolYearCycleSelector.list_by_school(school_id=int(school_id))
        serializer = SchoolYearCycleListSerializer(cycles, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get active cycles",
        description="Retrieve all cycle configurations for currently active school years.",
        tags=["School Operations - School Year Cycles"],
    )
    @action(detail=False, methods=["get"])
    def active(self, request):
        """Get cycles for active school years."""
        cycles = SchoolYearCycleSelector.list_active_cycles()
        serializer = SchoolYearCycleListSerializer(cycles, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Get active cycles by school",
        description="Retrieve cycle configurations for a school's active school year.",
        tags=["School Operations - School Year Cycles"],
    )
    @action(detail=False, methods=["get"], url_path="active/by-school/(?P<school_id>[^/.]+)")
    def active_by_school(self, request, school_id=None):
        """Get cycles for a school's active school year."""
        cycles = SchoolYearCycleSelector.list_by_school_and_active_year(
            school_id=int(school_id)
        )
        serializer = SchoolYearCycleListSerializer(cycles, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Bulk create cycles for school year",
        description="Create multiple cycle configurations for a school year at once.",
        tags=["School Operations - School Year Cycles"],
        request=SchoolYearCycleBulkCreateSerializer,
        responses={201: SchoolYearCycleListSerializer(many=True)},
    )
    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):
        """Bulk create cycle configurations for a school year."""
        serializer = SchoolYearCycleBulkCreateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        cycles = serializer.save()

        response_serializer = SchoolYearCycleListSerializer(cycles, many=True)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        summary="Restore a deleted cycle",
        description="Restore a soft-deleted school year cycle configuration.",
        tags=["School Operations - School Year Cycles"],
    )
    @action(detail=True, methods=["post"])
    def restore(self, request, id=None):
        """Restore a soft-deleted cycle."""
        cycle = self.get_object()

        if not cycle.is_deleted:
            return Response(
                {"detail": "Cycle is not deleted"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = request.user if request.user.is_authenticated else None
        restored_cycle = SchoolYearCycleService.restore(
            school_year_cycle=cycle,
            updated_by=user,
        )

        serializer = SchoolYearCycleSerializer(restored_cycle)
        return Response(serializer.data)
