from rest_framework.response import Response
from rest_framework.views import APIView

from domain.assessment.selectors import (
    AssessmentOverviewSelector,
    ClassroomGradingSelector,
    StudentGradesSelector,
)
from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin, IsTeacher, IsStudent


from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema

class AssessmentOverviewView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin | IsTeacher]
    serializer_class = None

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, assessment_id: int):
        data = AssessmentOverviewSelector.get_assessment_overview(assessment_id=assessment_id)
        return Response(data)


class ClassroomGradingSheetView(APIView):
    permission_classes = [IsTeacher]
    serializer_class = None

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, assessment_subject_id: int):
        data = ClassroomGradingSelector.get_classroom_grading_sheet(assessment_subject_id=assessment_subject_id)
        return Response(data)


class StudentGradesHistoryView(APIView):
    permission_classes = [IsStudent | IsSchoolStaffOrAdmin]
    serializer_class = None

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, enrollment_id: int):
        data = StudentGradesSelector.get_student_grades_history(student_enrollment_id=enrollment_id)
        return Response(data)


class ClassroomAveragesView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin | IsTeacher]
    serializer_class = None

    @extend_schema(responses=OpenApiTypes.OBJECT)
    def get(self, request, classroom_id: int):
        data = StudentGradesSelector.calculate_classroom_averages(classroom_id=classroom_id)
        return Response(data)
