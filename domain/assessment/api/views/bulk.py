from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.assessment.api.serializers import (
    AssessmentGradesCommitSerializer,
    AssessmentGradesPreviewSerializer,
)
from domain.assessment.services import StudentAssessmentService
from domain.enrollment.api.permissions import IsTeacher


class AssessmentSubjectGradesPreviewView(APIView):
    permission_classes = [IsTeacher]
    serializer_class = AssessmentGradesPreviewSerializer

    def post(self, request, assessment_subject_id: int):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = StudentAssessmentService.preview_bulk_import(
            assessment_subject_id=assessment_subject_id,
            grades=serializer.validated_data["grades"],
        )
        return Response(result, status=status.HTTP_200_OK)


class AssessmentSubjectGradesCommitView(APIView):
    permission_classes = [IsTeacher]
    serializer_class = AssessmentGradesCommitSerializer

    def post(self, request, assessment_subject_id: int):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = StudentAssessmentService.commit_bulk_import(
            assessment_subject_id=assessment_subject_id,
            grades=serializer.validated_data["grades"],
            user=request.user,
        )
        return Response(result, status=status.HTTP_200_OK)
