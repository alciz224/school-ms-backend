from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.assessment.api.serializers.reporting import (
    ReportCardGenerateSerializer,
    ReportCardSerializer,
    TranscriptGenerateSerializer,
    TranscriptSerializer,
)
from domain.assessment.selectors import ReportCardSelector, TranscriptSelector
from domain.assessment.services import ReportCardService, TranscriptService
from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin, IsStudent
from domain.enrollment.models import Classroom, StudentEnrollment
from domain.school_operations.models import SchoolYear, SchoolYearCycleTerm


class ReportCardGenerateView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = ReportCardGenerateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        classroom = Classroom.objects.get(id=serializer.validated_data["classroom_id"])
        term = SchoolYearCycleTerm.objects.get(id=serializer.validated_data["term_id"])
        result = ReportCardService.generate_for_classroom_term(
            classroom=classroom,
            term=term,
            user=request.user,
            force=serializer.validated_data.get("force", False),
        )
        return Response({
            "report_cards_created": result.report_cards_created,
            "report_cards_updated": result.report_cards_updated,
            "subjects_created": result.subjects_created,
        }, status=status.HTTP_200_OK)


class ReportCardDetailView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin | IsStudent]
    serializer_class = ReportCardSerializer

    def get(self, request, enrollment_id: int, term_id: int):
        rc = ReportCardSelector.get_for_student_term(
            student_enrollment_id=enrollment_id,
            term_id=term_id,
        )
        return Response(self.serializer_class(rc).data)


class ReportCardClassroomListView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = ReportCardSerializer

    def get(self, request, classroom_id: int, term_id: int):
        rcs = ReportCardSelector.list_for_classroom_term(
            classroom_id=classroom_id,
            term_id=term_id,
        )
        return Response(self.serializer_class(rcs, many=True).data)


class TranscriptGenerateView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]
    serializer_class = TranscriptGenerateSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        enrollment = StudentEnrollment.objects.get(id=serializer.validated_data["student_enrollment_id"])
        school_year = SchoolYear.objects.get(id=serializer.validated_data["school_year_id"])

        transcript = TranscriptService.generate_for_student(
            student_enrollment=enrollment,
            school_year=school_year,
            user=request.user,
        )
        # Note: Response uses TranscriptSerializer, explicitly set for schema if needed or just use serializer_class for request
        return Response(TranscriptSerializer(transcript).data, status=status.HTTP_200_OK)


class TranscriptDetailView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin | IsStudent]
    serializer_class = TranscriptSerializer

    def get(self, request, enrollment_id: int, school_year_id: int):
        tr = TranscriptSelector.get_for_student_year(
            student_enrollment_id=enrollment_id,
            school_year_id=school_year_id,
        )
        return Response(self.serializer_class(tr).data)
