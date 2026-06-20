from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.shared.exceptions import NotFoundException
from portal.school_admin.api.selectors import SchoolAdminParentSelector
from portal.school_admin.api.serializers import SchoolAdminParentSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SchoolAdminParentListView(APIView):
    """
    List and filter parents for the school admin portal.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, required=False),
            OpenApiParameter("has_email", OpenApiTypes.BOOL, required=False),
            OpenApiParameter("has_phone", OpenApiTypes.BOOL, required=False),
        ],
        responses=SchoolAdminParentSerializer(many=True),
    )
    def get(self, request):
        search = request.query_params.get("search")
        
        has_email_str = request.query_params.get("has_email")
        has_email = None
        if has_email_str is not None:
            has_email = has_email_str.lower() == 'true'
            
        has_phone_str = request.query_params.get("has_phone")
        has_phone = None
        if has_phone_str is not None:
            has_phone = has_phone_str.lower() == 'true'

        qs_list = SchoolAdminParentSelector.list(
            search=search,
            has_email=has_email,
            has_phone=has_phone,
        )

        # Basic pagination on a list
        paginator = StandardResultsSetPagination()
        # Since qs_list is a list, we might need a custom paginator or let DRF paginate it
        # DRF's PageNumberPagination expects a QuerySet or a list
        page = paginator.paginate_queryset(qs_list, request, view=self)
        if page is not None:
            serializer = SchoolAdminParentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SchoolAdminParentSerializer(qs_list, many=True)
        return Response(serializer.data)


class SchoolAdminParentDetailView(APIView):
    """
    Retrieve a specific parent by ID for the school admin portal.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolAdminParentSerializer)
    def get(self, request, pk):
        try:
            # Reusing the selector logic to maintain annotations
            qs_list = SchoolAdminParentSelector.list()
            parent = next((p for p in qs_list if str(p.id) == str(pk)), None)
            
            if not parent:
                raise NotFoundException("Parent", pk)
                
            serializer = SchoolAdminParentSerializer(parent)
            return Response(serializer.data)
        except ValueError:
            raise NotFoundException("Parent", pk)
