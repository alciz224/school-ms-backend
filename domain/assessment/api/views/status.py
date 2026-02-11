from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.assessment.models import Assessment, AssessmentSubject
from domain.assessment.services import AssessmentService, AssessmentSubjectService
from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin


class AssessmentStatusView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def post(self, request, assessment_id: int, action_name: str):
        obj = Assessment.objects.get(id=assessment_id)
        if action_name == "activate":
            obj = AssessmentService.activate(obj=obj, user=request.user)
        elif action_name == "close":
            obj = AssessmentService.close(obj=obj, user=request.user)
        elif action_name == "archive":
            obj = AssessmentService.archive(obj=obj, user=request.user)
        else:
            return Response({"detail": "Unknown action"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": obj.id, "status": obj.status})


class AssessmentSubjectStatusView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def post(self, request, assessment_subject_id: int, action_name: str):
        obj = AssessmentSubject.objects.get(id=assessment_subject_id)
        if action_name == "publish":
            obj = AssessmentSubjectService.publish(obj=obj, user=request.user)
        elif action_name == "close":
            obj = AssessmentSubjectService.close(obj=obj, user=request.user)
        elif action_name == "archive":
            obj = AssessmentSubjectService.archive(obj=obj, user=request.user)
        else:
            return Response({"detail": "Unknown action"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"id": obj.id, "status": obj.status})
