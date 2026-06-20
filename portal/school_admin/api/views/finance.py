from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from drf_spectacular.utils import extend_schema

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.finance.api.serializers.fee_summary import FeeSummarySerializer
from domain.finance.api.serializers.fee_type import FeeTypeSerializer
from domain.finance.api.serializers.school_fee import (
    SchoolFeeCreateSerializer,
    SchoolFeeSerializer,
    SchoolFeeUpdateSerializer,
)
from domain.finance.api.serializers.student_payment import (
    StudentPaymentCreateSerializer,
    StudentPaymentSerializer,
)
from domain.finance.selectors.fee_summary import FeeSummarySelector
from domain.finance.selectors.fee_type import FeeTypeSelector
from domain.finance.selectors.school_fee import SchoolFeeSelector
from domain.finance.services.school_fee import SchoolFeeService
from domain.finance.services.student_payment import StudentPaymentService


@extend_schema(responses=FeeTypeSerializer(many=True))
class FeeTypeListView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request):
        qs = FeeTypeSelector.list_active()
        serializer = FeeTypeSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})


@extend_schema(
    request=SchoolFeeCreateSerializer,
    responses=SchoolFeeSerializer,
)
class SchoolFeeCreateView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def post(self, request):
        serializer = SchoolFeeCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            school_fee = SchoolFeeService.create(
                school_year_id=d["school_year_id"],
                school_year_level_id=d["school_year_level_id"],
                fee_type_id=d["fee_type_id"],
                amount=d["amount"],
                due_date=d["due_date"],
                school_year_cycle_id=d.get("school_year_cycle_id"),
                is_mandatory=d.get("is_mandatory", True),
                created_by=request.user,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        output = SchoolFeeSerializer(school_fee)
        return Response({"success": True, "data": output.data}, status=status.HTTP_201_CREATED)


@extend_schema(
    request=SchoolFeeUpdateSerializer,
    responses=SchoolFeeSerializer,
)
class SchoolFeeUpdateView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def patch(self, request, pk=None):
        school_fee = SchoolFeeSelector.get_by_id(pk)
        if not school_fee:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "School fee not found."}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = SchoolFeeUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            school_fee = SchoolFeeService.update(
                school_fee=school_fee,
                amount=d.get("amount"),
                due_date=d.get("due_date"),
                is_mandatory=d.get("is_mandatory"),
                updated_by=request.user,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        output = SchoolFeeSerializer(school_fee)
        return Response({"success": True, "data": output.data})


@extend_schema(
    request=StudentPaymentCreateSerializer,
    responses=StudentPaymentSerializer,
)
class StudentPaymentCreateView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def post(self, request):
        serializer = StudentPaymentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            payment = StudentPaymentService.create(
                student_enrollment_id=d["student_enrollment_id"],
                school_fee_id=d["school_fee_id"],
                amount_paid=d["amount_paid"],
                payment_date=d["payment_date"],
                payment_method=d["payment_method"],
                reference_number=d.get("reference_number") or None,
                collected_by=d.get("collected_by") or None,
                notes=d.get("notes") or None,
                created_by=request.user,
            )
        except Exception as e:
            return Response(
                {"success": False, "error": {"code": "validation_error", "message": str(e)}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        output = StudentPaymentSerializer(payment)
        return Response({"success": True, "data": output.data}, status=status.HTTP_201_CREATED)


@extend_schema(responses=FeeSummarySerializer(many=True))
class FeeSummaryListView(APIView):
    permission_classes = [IsSchoolStaffOrAdmin]

    def get(self, request):
        school_year_id = request.query_params.get("school_year_id")
        if not school_year_id:
            return Response(
                {"success": False, "error": {"code": "missing_param", "message": "school_year_id is required."}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        classroom_id = request.query_params.get("classroom_id")
        data = FeeSummarySelector.get_summaries(
            school_year_id=school_year_id,
            classroom_id=classroom_id,
        )
        serializer = FeeSummarySerializer(data, many=True)
        return Response({"success": True, "data": serializer.data})
