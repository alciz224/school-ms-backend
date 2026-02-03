"""
AdministrativeUnit API views.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from domain.geography.models import RegionAdministrative, AdministrativeUnit
from domain.geography.services import AdministrativeUnitService
from domain.geography.selectors import AdministrativeUnitSelector
from domain.geography.api.serializers import (
    AdministrativeUnitListSerializer,
    AdministrativeUnitDetailSerializer,
    AdministrativeUnitCreateSerializer,
    AdministrativeUnitUpdateSerializer,
)
from domain.shared.api.responses import api_response


class AdministrativeUnitViewSet(viewsets.ViewSet):
    """
    ViewSet for AdministrativeUnit CRUD operations.

    list: GET /api/v1/administrative-units/
    create: POST /api/v1/administrative-units/
    retrieve: GET /api/v1/administrative-units/{id}/
    update: PUT /api/v1/administrative-units/{id}/
    partial_update: PATCH /api/v1/administrative-units/{id}/
    destroy: DELETE /api/v1/administrative-units/{id}/
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get base queryset with annotations."""
        return AdministrativeUnit.objects.select_related(
            'region', 'parent'
        ).annotate(
            localities_count=Count('localities', filter=Q(localities__is_deleted=False)),
            children_count=Count('children', filter=Q(children__is_deleted=False))
        )

    def list(self, request):
        """List all administrative units."""
        queryset = self.get_queryset().order_by('region__name', 'type', 'name')
        
        # Optional filters
        region_id = request.query_params.get('region_id')
        if region_id:
            queryset = queryset.filter(region_id=region_id)
        
        unit_type = request.query_params.get('type')
        if unit_type:
            queryset = queryset.filter(type=unit_type.upper())
        
        parent_id = request.query_params.get('parent_id')
        if parent_id:
            queryset = queryset.filter(parent_id=parent_id)
        
        # Filter for root units only
        root_only = request.query_params.get('root_only')
        if root_only and root_only.lower() == 'true':
            queryset = queryset.filter(parent__isnull=True)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        serializer = AdministrativeUnitListSerializer(queryset, many=True)
        return api_response(data=serializer.data)

    def create(self, request):
        """Create a new administrative unit."""
        serializer = AdministrativeUnitCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        region = RegionAdministrative.objects.get(
            id=serializer.validated_data['region_id']
        )
        parent = None
        if serializer.validated_data.get('parent_id'):
            parent = AdministrativeUnit.objects.get(
                id=serializer.validated_data['parent_id']
            )
        
        unit = AdministrativeUnitService.create(
            region=region,
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            unit_type=serializer.validated_data['type'],
            parent=parent,
            user=request.user
        )
        
        # Re-fetch with annotations
        unit = self.get_queryset().get(id=unit.id)
        output_serializer = AdministrativeUnitDetailSerializer(unit)
        return api_response(
            data=output_serializer.data,
            message='Administrative unit created successfully.',
            status_code=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """Get an administrative unit by ID."""
        unit = self.get_queryset().filter(id=pk).first()
        if not unit:
            return api_response(
                success=False,
                message='Administrative unit not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdministrativeUnitDetailSerializer(unit)
        return api_response(data=serializer.data)

    def update(self, request, pk=None):
        """Update an administrative unit."""
        unit = AdministrativeUnit.objects.filter(id=pk).first()
        if not unit:
            return api_response(
                success=False,
                message='Administrative unit not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = AdministrativeUnitUpdateSerializer(data=request.data, unit=unit)
        serializer.is_valid(raise_exception=True)
        
        parent = None
        parent_id = serializer.validated_data.get('parent_id')
        if parent_id:
            parent = AdministrativeUnit.objects.get(id=parent_id)
        
        unit = AdministrativeUnitService.update(
            unit=unit,
            code=serializer.validated_data.get('code'),
            name=serializer.validated_data.get('name'),
            unit_type=serializer.validated_data.get('type'),
            parent=parent,
            user=request.user
        )
        
        # Re-fetch with annotations
        unit = self.get_queryset().get(id=unit.id)
        output_serializer = AdministrativeUnitDetailSerializer(unit)
        return api_response(
            data=output_serializer.data,
            message='Administrative unit updated successfully.'
        )

    def partial_update(self, request, pk=None):
        """Partially update an administrative unit."""
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """Delete an administrative unit (soft delete)."""
        unit = AdministrativeUnit.objects.filter(id=pk).first()
        if not unit:
            return api_response(
                success=False,
                message='Administrative unit not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            AdministrativeUnitService.delete(unit=unit, user=request.user)
            return api_response(
                message='Administrative unit deleted successfully.',
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
