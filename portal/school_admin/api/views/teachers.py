from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.decorators import action

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.account.models import CustomUser
from domain.school_operations.models import SchoolYearTeacher
from domain.enrollment.models import TeacherAssignment, StudentEnrollment

from portal.school_admin.api.serializers import (
    TeacherSerializer,
    SchoolYearTeacherSerializer,
    TeacherAssignmentSerializer,
    TeacherClassSerializer,
)

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TeacherListView(APIView):
    """
    List all teachers.
    In this system, a teacher is a CustomUser who has at least one SchoolYearTeacher record,
    or has a 'TEACHER' role if we filter by that.
    For the portal, we return all users who are linked to SchoolYearTeacher.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=TeacherSerializer(many=True))
    def get(self, request):
        # We find all distinct users who have a SchoolYearTeacher record
        teacher_ids = SchoolYearTeacher.objects.filter(is_deleted=False).values_list('teacher_id', flat=True).distinct()
        qs = CustomUser.objects.filter(id__in=teacher_ids, is_active=True).order_by("first_name", "last_name")
        
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(qs, request, view=self)
        if page is not None:
            serializer = TeacherSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = TeacherSerializer(qs, many=True)
        return Response(serializer.data)


class SchoolYearTeacherViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SchoolYearTeacher operations.
    """
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = SchoolYearTeacherSerializer
    queryset = SchoolYearTeacher.objects.filter(is_deleted=False).select_related("teacher")
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        qs = super().get_queryset()
        school_year_id = self.request.query_params.get("school_year_id")
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        return qs

    @extend_schema(responses=TeacherAssignmentSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="assignments")
    def assignments(self, request, pk=None):
        """Get assignments for this specific school_year_teacher."""
        syt = self.get_object()
        assignments = TeacherAssignment.objects.filter(
            school_year_teacher=syt, is_deleted=False
        ).select_related(
            "classroom",
            "school_year_level_subject__subject",
            "school_year_level_subject__school_year_level__level",
            "school_year_level_subject__school_year_level__track",
        ).order_by("-start_date")
        serializer = TeacherAssignmentSerializer(assignments, many=True)
        return Response(serializer.data)


class SchoolYearTeacherBySchoolYearView(APIView):
    """
    List teachers for a specific school year.
    Matches the GET /school-years/{id}/teachers/ route.
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=SchoolYearTeacherSerializer(many=True))
    def get(self, request, school_year_id):
        qs = SchoolYearTeacher.objects.filter(
            school_year_id=school_year_id, is_deleted=False
        ).select_related("teacher__user").order_by("teacher__user__first_name", "teacher__user__last_name")
        
        serializer = SchoolYearTeacherSerializer(qs, many=True)
        return Response(serializer.data)


class TeacherAssignmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for TeacherAssignment operations.
    """
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = TeacherAssignmentSerializer
    queryset = TeacherAssignment.objects.filter(is_deleted=False).select_related(
        "classroom",
        "school_year_level_subject__subject",
        "school_year_level_subject__school_year_level__level",
        "school_year_level_subject__school_year_level__track",
    )
    pagination_class = StandardResultsSetPagination


class TeacherClassesView(APIView):
    """
    List classes taught by a teacher.
    Matches GET /teachers/{teacher_id}/classes/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("teacher_id", OpenApiTypes.STR, required=False),
            OpenApiParameter("school_year_id", OpenApiTypes.STR, required=False),
        ],
        responses=TeacherClassSerializer(many=True),
    )
    def get(self, request, teacher_id=None):
        teacher_id = teacher_id or request.query_params.get("teacher_id")
        school_year_id = request.query_params.get("school_year_id")

        if not teacher_id:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": "teacher_id is required"}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        qs = TeacherAssignment.objects.filter(
            is_deleted=False,
            school_year_teacher__teacher_id=teacher_id,
            assignment_status="ACTIVE",
        ).select_related(
            "classroom",
            "school_year_level_subject__subject",
            "school_year_level_subject__school_year_level__level",
            "school_year_level_subject__school_year_level__track",
        )

        if school_year_id:
            qs = qs.filter(school_year_teacher__school_year_id=school_year_id)

        classes_data = []
        seen_classrooms = set()
        classroom_students = {}
        for ta in qs:
            if ta.classroom_id not in classroom_students:
                classroom_students[ta.classroom_id] = StudentEnrollment.objects.filter(
                    is_deleted=False, classroom_id=ta.classroom_id, enrollment_status="ACTIVE"
                ).count()

            class_key = f"{ta.classroom_id}_{ta.school_year_level_subject.subject_id}"
            if class_key in seen_classrooms:
                continue
            seen_classrooms.add(class_key)

            color_map = {"MATHEMATIQUES": "blue", "FRANCAIS": "green", "PHYSIQUE": "red",
                         "ANGLAIS": "yellow", "HISTOIRE": "purple", "GEOGRAPHIE": "orange"}
            subject_name = ta.school_year_level_subject.subject.name.upper() if ta.school_year_level_subject.subject else ""

            classes_data.append({
                "id": str(ta.classroom.id),
                "name": ta.classroom.name,
                "subject": subject_name,
                "level": ta.school_year_level_subject.school_year_level.level.name if ta.school_year_level_subject.school_year_level.level else "",
                "students": classroom_students[ta.classroom_id],
                "color": color_map.get(subject_name.split()[0], "blue"),
                "assignment_id": str(ta.id),
            })

        serializer = TeacherClassSerializer(classes_data, many=True)
        return Response({"success": True, "data": serializer.data})
