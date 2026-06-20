from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.assessment.models import Assessment, AssessmentSubject, StudentAssessment
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus

from portal.school_admin.api.serializers.assessment import (
    AssessmentSerializer,
    AssessmentDetailSerializer,
    AssessmentSubjectSerializer,
    AssessmentSubjectDetailSerializer,
    StudentAssessmentSerializer,
    StudentGradeSerializer,
)

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    CRUD for Assessment sessions.
    """
    permission_classes = [IsSchoolStaffOrAdmin]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AssessmentDetailSerializer
        return AssessmentSerializer

    def get_queryset(self):
        qs = Assessment.objects.filter(is_deleted=False).select_related(
            "school_year",
            "school_year_cycle",
            "school_year_cycle_term",
            "assessment_type",
            "school_year_cycle__cycle",
            "school_year_cycle_term__term",
        )
        school_year_cycle_id = self.request.query_params.get("school_year_cycle_id")
        school_year_cycle_term_id = self.request.query_params.get("school_year_cycle_term_id")
        status_param = self.request.query_params.get("status")
        if school_year_cycle_id:
            qs = qs.filter(school_year_cycle_id=school_year_cycle_id)
        if school_year_cycle_term_id:
            qs = qs.filter(school_year_cycle_term_id=school_year_cycle_term_id)
        if status_param:
            qs = qs.filter(status=status_param.upper())
        return qs.order_by("-start_date")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)

    @extend_schema(responses=AssessmentSubjectSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="subjects")
    def subjects(self, request, id=None):
        assessment = self.get_object()
        subjects = AssessmentSubject.objects.filter(
            is_deleted=False, assessment=assessment
        ).select_related(
            "classroom",
            "school_year_level_subject__subject",
            "school_year_level_subject__school_year_level__level",
            "teacher_assignment__school_year_teacher__teacher",
        )
        serializer = AssessmentSubjectSerializer(subjects, many=True)
        return Response({"success": True, "data": serializer.data})


class AssessmentSubjectViewSet(viewsets.ModelViewSet):
    """
    CRUD for assessment subjects (exams).
    """
    permission_classes = [IsSchoolStaffOrAdmin]
    lookup_field = "id"

    def get_serializer_class(self):
        if self.action == "retrieve":
            return AssessmentSubjectDetailSerializer
        return AssessmentSubjectSerializer

    def get_queryset(self):
        qs = AssessmentSubject.objects.filter(is_deleted=False).select_related(
            "assessment",
            "classroom",
            "school_year_level_subject__subject",
            "school_year_level_subject__school_year_level__level",
            "school_year_level_subject__school_year_level__track",
            "teacher_assignment__school_year_teacher__teacher",
        )
        assessment_id = self.request.query_params.get("assessment_id")
        if assessment_id:
            qs = qs.filter(assessment_id=assessment_id)
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    def perform_destroy(self, instance):
        instance.soft_delete(user=self.request.user)

    @extend_schema(responses=StudentGradeSerializer(many=True))
    @action(detail=True, methods=["get"], url_path="grades")
    def grades(self, request, id=None):
        subject = self.get_object()
        grades = StudentAssessment.objects.filter(
            is_deleted=False, assessment_subject=subject
        ).select_related(
            "student_enrollment__student",
        )
        serializer = StudentGradeSerializer(grades, many=True)
        return Response({"success": True, "data": serializer.data})


class StudentAssessmentViewSet(viewsets.ModelViewSet):
    """
    Update individual student assessments.
    """
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = StudentAssessmentSerializer
    lookup_field = "id"

    def get_queryset(self):
        return StudentAssessment.objects.filter(is_deleted=False).select_related(
            "assessment_subject",
            "student_enrollment__student",
        )

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)

    @extend_schema(
        request=StudentAssessmentSerializer(many=True),
        responses=StudentGradeSerializer(many=True),
    )
    @action(detail=False, methods=["post"], url_path="bulk-update")
    def bulk_update(self, request):
        data = request.data if isinstance(request.data, list) else [request.data]
        updated = []
        for item in data:
            pk = item.get("id")
            if not pk:
                continue
            try:
                instance = StudentAssessment.objects.get(id=pk, is_deleted=False)
                serializer = StudentAssessmentSerializer(
                    instance, data=item, partial=True, context={"request": request}
                )
                serializer.is_valid(raise_exception=True)
                serializer.save(updated_by=request.user)
                updated.append(serializer.data)
            except StudentAssessment.DoesNotExist:
                continue
        return Response({"success": True, "data": updated})


class StudentEnrollmentGradesView(APIView):
    """
    Get all grades for a specific enrollment.
    Matches GET /students/enrollments/{enrollmentId}/grades/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=StudentGradeSerializer(many=True))
    def get(self, request, enrollment_id=None):
        grades = StudentAssessment.objects.filter(
            is_deleted=False,
            student_enrollment_id=enrollment_id,
        ).select_related(
            "assessment_subject__school_year_level_subject__subject",
            "assessment_subject__classroom",
        )
        serializer = StudentGradeSerializer(grades, many=True)
        return Response({"success": True, "data": serializer.data})
