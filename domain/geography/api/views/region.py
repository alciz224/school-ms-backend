"""
RegionAdministrative API views.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from domain.geography.models import Country, RegionAdministrative
from domain.geography.services import RegionService
from domain.geography.selectors import RegionSelector
from domain.geography.api.serializers import (
    RegionListSerializer,
    RegionDetailSerializer,
    RegionCreateSerializer,
    RegionUpdateSerializer,
)
from domain.shared.api.responses import api_response


class RegionViewSet(viewsets.ViewSet):
    """
    ViewSet for RegionAdministrative CRUD operations.

    list: GET /api/v1/regions/
    create: POST /api/v1/regions/
    retrieve: GET /api/v1/regions/{id}/
    update: PUT /api/v1/regions/{id}/
    partial_update: PATCH /api/v1/regions/{id}/
    destroy: DELETE /api/v1/regions/{id}/
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get base queryset with annotations."""
        return RegionAdministrative.objects.select_related('country').annotate(
            administrative_units_count=Count(
                'administrative_units', 
                filter=Q(administrative_units__is_deleted=False)
            )
        )

    def list(self, request):
        """List all regions."""
        queryset = self.get_queryset().order_by('country__name', 'name')
        
        # Optional filters
        country_id = request.query_params.get('country_id')
        if country_id:
            queryset = queryset.filter(country_id=country_id)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        serializer = RegionListSerializer(queryset, many=True)
        return api_response(data=serializer.data)

    def create(self, request):
        """Create a new region."""
        serializer = RegionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        country = Country.objects.get(id=serializer.validated_data['country_id'])
        
        region = RegionService.create(
            country=country,
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description'),
            user=request.user
        )
        
        # Re-fetch with annotations
        region = self.get_queryset().get(id=region.id)
        output_serializer = RegionDetailSerializer(region)
        return api_response(
            data=output_serializer.data,
            message='Region created successfully.',
            status_code=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """Get a region by ID."""
        region = self.get_queryset().filter(id=pk).first()
        if not region:
            return api_response(
                success=False,
                message='Region not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RegionDetailSerializer(region)
        return api_response(data=serializer.data)

    def update(self, request, pk=None):
        """Update a region."""
        region = RegionAdministrative.objects.filter(id=pk).first()
        if not region:
            return api_response(
                success=False,
                message='Region not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RegionUpdateSerializer(data=request.data, region=region)
        serializer.is_valid(raise_exception=True)
        
        region = RegionService.update(
            region=region,
            code=serializer.validated_data.get('code'),
            name=serializer.validated_data.get('name'),
            description=serializer.validated_data.get('description'),
            user=request.user
        )
        
        # Re-fetch with annotations
        region = self.get_queryset().get(id=region.id)
        output_serializer = RegionDetailSerializer(region)
        return api_response(
            data=output_serializer.data,
            message='Region updated successfully.'
        )

    def partial_update(self, request, pk=None):
        """Partially update a region."""
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """Delete a region (soft delete)."""
        region = RegionAdministrative.objects.filter(id=pk).first()
        if not region:
            return api_response(
                success=False,
                message='Region not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            RegionService.delete(region=region, user=request.user)
            return api_response(
                message='Region deleted successfully.',
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
