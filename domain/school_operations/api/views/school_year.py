"""
SchoolYear API views.
"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from domain.school_operations.models import School, SchoolYear
from domain.school_operations.api.serializers.school_year import (
    SchoolYearListSerializer,
    SchoolYearDetailSerializer,
    SchoolYearCreateSerializer,
    SchoolYearUpdateSerializer,
    SchoolYearStatusSerializer,
    SchoolYearHolidaySerializer,
    SchoolYearSettingSerializer,
    SchoolYearStatisticsSerializer,
)
from domain.school_operations.selectors.school_year import SchoolYearSelector
from domain.school_operations.services.school_year import SchoolYearService
from domain.academic.models import AcademicYear


class SchoolYearViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SchoolYear operations.
    
    Endpoints:
        - GET /api/school-years/ - List school years
        - POST /api/school-years/ - Create school year
        - GET /api/school-years/{id}/ - Retrieve school year
        - PUT /api/school-years/{id}/ - Update school year
        - PATCH /api/school-years/{id}/ - Partial update
        - DELETE /api/school-years/{id}/ - Soft delete school year
        
    Custom Actions:
        - POST /api/school-years/{id}/activate/ - Activate school year
        - POST /api/school-years/{id}/complete/ - Complete school year
        - POST /api/school-years/{id}/archive/ - Archive school year
        - POST /api/school-years/{id}/add-holiday/ - Add holiday
        - POST /api/school-years/{id}/update-setting/ - Update setting
        - GET /api/school-years/{id}/statistics/ - Get statistics
        - GET /api/school-years/current/ - Get current school years
        - GET /api/school-years/active/ - Get active school years
        - GET /api/school-years/open-enrollment/ - Get years with open enrollment
    """
    
    permission_classes = [IsAuthenticated]
    queryset = SchoolYear.objects.all()
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return SchoolYearListSerializer
        elif self.action == 'create':
            return SchoolYearCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SchoolYearUpdateSerializer
        elif self.action == 'change_status':
            return SchoolYearStatusSerializer
        elif self.action == 'add_holiday':
            return SchoolYearHolidaySerializer
        elif self.action == 'update_setting':
            return SchoolYearSettingSerializer
        elif self.action == 'statistics':
            return SchoolYearStatisticsSerializer
        return SchoolYearDetailSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters."""
        queryset = SchoolYear.objects.all().select_related(
            'school',
            'academic_year',
            'created_by',
            'updated_by'
        )
        
        # Filter by school
        school_id = self.request.query_params.get('school')
        if school_id:
            queryset = queryset.filter(school_id=school_id)
        
        # Filter by academic year
        academic_year_id = self.request.query_params.get('academic_year')
        if academic_year_id:
            queryset = queryset.filter(academic_year_id=academic_year_id)
        
        # Filter by status
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        
        # Filter by current
        is_current = self.request.query_params.get('is_current')
        if is_current is not None:
            queryset = queryset.filter(is_current=is_current.lower() == 'true')
        
        # Search
        search = self.request.query_params.get('search')
        if search:
            queryset = SchoolYearSelector.search(search)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create school year with user tracking."""
        serializer.save()
    
    def perform_update(self, serializer):
        """Update school year with user tracking."""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete school year."""
        SchoolYearService.delete_school_year(
            school_year=instance,
            user=self.request.user
        )
    
    @action(detail=False, methods=['get'])
    def current(self, request):
        """Get current school years."""
        school_id = request.query_params.get('school')
        
        if school_id:
            school = get_object_or_404(School, id=school_id)
            school_year = SchoolYearSelector.get_current_for_school(school)
            if school_year:
                serializer = self.get_serializer(school_year)
                return Response(serializer.data)
            return Response(
                {'detail': 'No current school year found for this school.'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            queryset = SchoolYear.objects.filter(is_current=True)
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get active school years."""
        queryset = SchoolYearSelector.list_active()
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='open-enrollment')
    def open_enrollment(self, request):
        """Get school years with open enrollment."""
        queryset = SchoolYearSelector.list_with_open_enrollment()
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate a school year."""
        school_year = self.get_object()
        
        try:
            SchoolYearService.activate_school_year(
                school_year=school_year,
                user=request.user
            )
            serializer = self.get_serializer(school_year)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark school year as completed."""
        school_year = self.get_object()
        
        try:
            SchoolYearService.complete_school_year(
                school_year=school_year,
                user=request.user
            )
            serializer = self.get_serializer(school_year)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a school year."""
        school_year = self.get_object()
        
        try:
            SchoolYearService.archive_school_year(
                school_year=school_year,
                user=request.user
            )
            serializer = self.get_serializer(school_year)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='add-holiday')
    def add_holiday(self, request, pk=None):
        """Add a holiday to school year."""
        school_year = self.get_object()
        serializer = SchoolYearHolidaySerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                SchoolYearService.add_holiday_to_school_year(
                    school_year=school_year,
                    name=serializer.validated_data['name'],
                    start_date=serializer.validated_data['start_date'],
                    end_date=serializer.validated_data.get('end_date'),
                    user=request.user
                )
                detail_serializer = SchoolYearDetailSerializer(school_year)
                return Response(detail_serializer.data)
            except Exception as e:
                return Response(
                    {'detail': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], url_path='update-setting')
    def update_setting(self, request, pk=None):
        """Update a school year setting."""
        school_year = self.get_object()
        serializer = SchoolYearSettingSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                SchoolYearService.update_school_year_setting(
                    school_year=school_year,
                    key=serializer.validated_data['key'],
                    value=serializer.validated_data['value'],
                    user=request.user
                )
                detail_serializer = SchoolYearDetailSerializer(school_year)
                return Response(detail_serializer.data)
            except Exception as e:
                return Response(
                    {'detail': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def statistics(self, request, pk=None):
        """Get enrollment statistics for school year."""
        school_year = self.get_object()
        
        stats = SchoolYearService.get_enrollment_statistics(school_year)
        serializer = SchoolYearStatisticsSerializer(stats)
        
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-school/(?P<school_id>[^/.]+)')
    def by_school(self, request, school_id=None):
        """Get all school years for a specific school."""
        school = get_object_or_404(School, id=school_id)
        
        include_archived = request.query_params.get('include_archived', 'false').lower() == 'true'
        status_filter = request.query_params.get('status')
        
        queryset = SchoolYearSelector.list_by_school(
            school=school,
            status=status_filter,
            include_archived=include_archived
        )
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='by-academic-year/(?P<academic_year_id>[^/.]+)')
    def by_academic_year(self, request, academic_year_id=None):
        """Get all school years for a specific academic year."""
        academic_year = get_object_or_404(AcademicYear, id=academic_year_id)
        
        status_filter = request.query_params.get('status')
        
        queryset = SchoolYearSelector.list_by_academic_year(
            academic_year=academic_year,
            status=status_filter
        )
        
        # Pagination
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
