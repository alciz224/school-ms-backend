from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.shared.exceptions import NotFoundException
from portal.school_admin.api.selectors import SchoolAdminStudentSelector
from portal.school_admin.api.serializers import SchoolAdminStudentSerializer

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class SchoolAdminStudentListView(APIView):
    """
    List and filter students for the school admin portal.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("search", OpenApiTypes.STR, required=False),
            OpenApiParameter("academic_year", OpenApiTypes.STR, required=False),
            OpenApiParameter("cycle", OpenApiTypes.STR, required=False),
            OpenApiParameter("level", OpenApiTypes.STR, required=False),
            OpenApiParameter("class_name", OpenApiTypes.STR, required=False),
            OpenApiParameter("status", OpenApiTypes.STR, required=False),
            OpenApiParameter("gender", OpenApiTypes.STR, required=False),
        ],
        responses=SchoolAdminStudentSerializer(many=True),
    )
    def get(self, request):
        search = request.query_params.get("search")
        academic_year = request.query_params.get("academic_year")
        cycle = request.query_params.get("cycle")
        level = request.query_params.get("level")
        class_name = request.query_params.get("class_name")
        status_param = request.query_params.get("status")
        gender = request.query_params.get("gender")

        qs = SchoolAdminStudentSelector.list(
            search=search,
            academic_year=academic_year,
            cycle=cycle,
            level=level,
            class_name=class_name,
            status=status_param,
            gender=gender,
        )

        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        if page is not None:
            serializer = SchoolAdminStudentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = SchoolAdminStudentSerializer(qs, many=True)
        return Response(serializer.data)


class SchoolAdminStudentDetailView(APIView):
    """
    Retrieve a specific student by ID for the school admin portal.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolAdminStudentSerializer)
    def get(self, request, pk):
        # Find the specific student enrollment. 
        # The frontend provides the enrollment ID or student User ID.
        # Assuming frontend passes the enrollment ID or we match by User ID.
        # Given our selector returns StudentEnrollments, the ID in the URL should match `student.id` or `enrollment.id`
        # Let's support both or just `enrollment.id` if that's what's passed.
        # Wait, the serializer maps `id` to `student.id`.
        qs = SchoolAdminStudentSelector.list()
        
        # Try to find by student.id first, if it fails, maybe enrollment ID?
        try:
            student_enrollment = qs.filter(student__id=pk).first()
            if not student_enrollment:
                # Try by enrollment ID
                student_enrollment = qs.filter(id=pk).first()
                
            if not student_enrollment:
                raise NotFoundException("Student", pk)
                
            serializer = SchoolAdminStudentSerializer(student_enrollment)
            return Response(serializer.data)
        except ValueError:
            raise NotFoundException("Student", pk)
