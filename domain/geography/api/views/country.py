"""
Country API views.
"""

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q

from domain.geography.models import Country
from domain.geography.services import CountryService
from domain.geography.selectors import CountrySelector
from domain.geography.api.serializers import (
    CountryListSerializer,
    CountryDetailSerializer,
    CountryCreateSerializer,
    CountryUpdateSerializer,
)
from domain.shared.api.responses import api_response


class CountryViewSet(viewsets.ViewSet):
    """
    ViewSet for Country CRUD operations.

    list: GET /api/v1/countries/
    create: POST /api/v1/countries/
    retrieve: GET /api/v1/countries/{id}/
    update: PUT /api/v1/countries/{id}/
    partial_update: PATCH /api/v1/countries/{id}/
    destroy: DELETE /api/v1/countries/{id}/
    """

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Get base queryset with annotations."""
        return Country.objects.annotate(
            regions_count=Count('regions', filter=Q(regions__is_deleted=False))
        )

    def list(self, request):
        """List all countries."""
        queryset = self.get_queryset().order_by('name')
        
        # Optional search filter
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        
        serializer = CountryListSerializer(queryset, many=True)
        return api_response(data=serializer.data)

    def create(self, request):
        """Create a new country."""
        serializer = CountryCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        country = CountryService.create(
            code=serializer.validated_data['code'],
            name=serializer.validated_data['name'],
            description=serializer.validated_data.get('description'),
            user=request.user
        )
        
        # Re-fetch with annotations
        country = self.get_queryset().get(id=country.id)
        output_serializer = CountryDetailSerializer(country)
        return api_response(
            data=output_serializer.data,
            message='Country created successfully.',
            status_code=status.HTTP_201_CREATED
        )

    def retrieve(self, request, pk=None):
        """Get a country by ID."""
        country = self.get_queryset().filter(id=pk).first()
        if not country:
            return api_response(
                success=False,
                message='Country not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CountryDetailSerializer(country)
        return api_response(data=serializer.data)

    def update(self, request, pk=None):
        """Update a country."""
        country = Country.objects.filter(id=pk).first()
        if not country:
            return api_response(
                success=False,
                message='Country not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        serializer = CountryUpdateSerializer(data=request.data, country=country)
        serializer.is_valid(raise_exception=True)
        
        country = CountryService.update(
            country=country,
            code=serializer.validated_data.get('code'),
            name=serializer.validated_data.get('name'),
            description=serializer.validated_data.get('description'),
            user=request.user
        )
        
        # Re-fetch with annotations
        country = self.get_queryset().get(id=country.id)
        output_serializer = CountryDetailSerializer(country)
        return api_response(
            data=output_serializer.data,
            message='Country updated successfully.'
        )

    def partial_update(self, request, pk=None):
        """Partially update a country."""
        return self.update(request, pk)

    def destroy(self, request, pk=None):
        """Delete a country (soft delete)."""
        country = Country.objects.filter(id=pk).first()
        if not country:
            return api_response(
                success=False,
                message='Country not found.',
                status_code=status.HTTP_404_NOT_FOUND
            )
        
        try:
            CountryService.delete(country=country, user=request.user)
            return api_response(
                message='Country deleted successfully.',
                status_code=status.HTTP_204_NO_CONTENT
            )
        except Exception as e:
            return api_response(
                success=False,
                message=str(e),
                status_code=status.HTTP_400_BAD_REQUEST
            )
