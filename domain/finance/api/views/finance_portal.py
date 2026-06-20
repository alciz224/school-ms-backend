from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.finance.api.serializers.fee_summary import FinanceStatsSerializer
from domain.finance.api.serializers.student_payment import StudentPaymentSerializer
from domain.finance.selectors.fee_summary import FeeSummarySelector
from domain.finance.selectors.payment import PaymentSelector


@extend_schema(responses=StudentPaymentSerializer(many=True))
class EnrollmentPaymentsListView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, student_enrollment_id=None):
        qs = PaymentSelector.list_by_enrollment(student_enrollment_id)
        serializer = StudentPaymentSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


@extend_schema(responses=StudentPaymentSerializer(many=True))
class ClassroomPaymentsListView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, classroom_id=None):
        qs = PaymentSelector.list_by_classroom(classroom_id)
        serializer = StudentPaymentSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


@extend_schema(responses=FinanceStatsSerializer)
class FinanceStatsView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request, school_year_id=None):
        data = FeeSummarySelector.get_stats(school_year_id=school_year_id)
        serializer = FinanceStatsSerializer(data)
        return Response({"success": True, "data": serializer.data})
