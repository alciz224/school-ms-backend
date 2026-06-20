from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from domain.finance.api.serializers.student_payment import (
    StudentPaymentCreateSerializer,
    StudentPaymentSerializer,
)
from domain.finance.selectors.payment import PaymentSelector
from domain.finance.services.student_payment import StudentPaymentService


class StudentPaymentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = StudentPaymentSerializer

    def get_queryset(self):
        enrollment_id = self.request.query_params.get("student_enrollment_id")
        if enrollment_id:
            return PaymentSelector.list_by_enrollment(enrollment_id)
        return PaymentSelector.list_by_school_year(
            self.request.query_params.get("school_year_id", 0)
        )

    def get_serializer_class(self):
        if self.action == "create":
            return StudentPaymentCreateSerializer
        return StudentPaymentSerializer

    def create(self, request, *args, **kwargs):
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
