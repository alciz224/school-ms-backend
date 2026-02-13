"""
Locality API views.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from domain.geography.models import AdministrativeUnit, Locality
from domain.geography.services import LocalityService
from domain.geography.selectors import LocalitySelector
from domain.geography.api.serializers import (
    LocalityListSerializer,
    LocalityDetailSerializer,
    LocalityCreateSerializer,
    LocalityUpdateSerializer,
)
from domain.shared.api.responses import api_response


class LocalityViewSet(viewsets.GenericViewSet):
    """
    ViewSet for Locality CRUD operations.

    list: GET /api/v1/localities/
    create: POST /api/v1/localities/
    retrieve: GET /api/v1/localities/{id}/
    update: PUT /api/v1/localities/{id}/
    partial_update: PATCH /api/v1/localities/{id}/
    destroy: DELETE /api/v1/localities/{id}/
    """

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return LocalityListSerializer
        elif self.action == 'create':
            return LocalityCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return LocalityUpdateSerializer
        return LocalityDetailSerializer

    def get_queryset(self):
        """Get base queryset with related data."""
        return Locality.objects.select_related(
            'administrative_unit',
            'administrative_unit__region',
            'administrative_unit__parent'
        )

    def list(self, request, *args, **kwargs):
        """List all localities."""
        queryset = self.get_queryset().order_by('administrative_unit__name', 'name')
        
        # Optional filters
        unit_id = request.query_params.get('administrative_unit_id')
        if unit_id:
            queryset = queryset.filter(administrative_unit_id=unit_id)
        
        region_id = request.query_params.get('region_id')
        if region_id:
            queryset = queryset.filter(administrative_unit__region_id=region_id)
        
        country_id = request.query_params.get('country_id')
        if country_id:
            queryset = queryset.filter(
                administrative_unit__region__country_id=country_id
            )
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        serializer = self.get_serializer(queryset, many=True)
        return api_response(data=serializer.data)

    def create(self, request, *args, **kwargs):
        """Create a new locality."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        unit = AdministrativeUnit.objects.get(
            id=serializer.validated_data['administrative_unit_id']
        )
        
        locality = LocalityService.create(
            administrative_unit=unit,
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            user=request.user
        )
        
        # Re-fetch with related data
        locality = self.get_queryset().get(id=locality.id)
        output_serializer = LocalityDetailSerializer(locality)
        return api_response(
            data=output_serializer.data,
            message='Locality created successfully.',
            status_code=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None, *args, **kwargs):
        """Get a locality by ID."""
        locality = self.get_queryset().filter(id=pk).first()
        if not locality:
            return api_response(
                success=False,
                message='Locality not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(locality)
        return api_response(data=serializer.data)

    def update(self, request, pk=None, *args, **kwargs):
        """Update a locality."""
        locality = Locality.objects.filter(id=pk).first()
        if not locality:
            return api_response(
                success=False,
                message='Locality not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = self.get_serializer(data=request.data, locality=locality)
        serializer.is_valid(raise_exception=True)
        
        unit = None
        unit_id = serializer.validated_data.get('administrative_unit_id')
        if unit_id:
            unit = AdministrativeUnit.objects.get(id=unit_id)
        
        locality = LocalityService.update(
            locality=locality,
            code=serializer.validated_data.get('code'),
            name=serializer.validated_data.get('name'),
            administrative_unit=unit,
            user=request.user
        )
        
        # Re-fetch with related data
        locality = self.get_queryset().get(id=locality.id)
        output_serializer = LocalityDetailSerializer(locality)
        return api_response(
            data=output_serializer.data,
            message='Locality updated successfully.'
        )

    def partial_update(self, request, pk=None):
        """Partially update a locality."""
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """Delete a locality (soft delete)."""
        locality = Locality.objects.filter(id=pk).first()
        if not locality:
            return api_response(
                success=False,
                message='Locality not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            LocalityService.delete(locality=locality, user=request.user)
            return api_response(
                message='Locality deleted successfully.',
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
