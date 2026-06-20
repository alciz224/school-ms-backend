from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from domain.finance.api.serializers.fee_summary import (
    FeeSummarySerializer,
    FinanceStatsSerializer,
)
from domain.finance.api.serializers.school_fee import (
    SchoolFeeCreateSerializer,
    SchoolFeeSerializer,
    SchoolFeeUpdateSerializer,
)
from domain.finance.selectors.fee_summary import FeeSummarySelector
from domain.finance.selectors.school_fee import SchoolFeeSelector
from domain.finance.services.school_fee import SchoolFeeService


class SchoolFeeViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = SchoolFeeSerializer

    def get_queryset(self):
        qs = SchoolFeeSelector.list_by_school_year(
            self.request.query_params.get("school_year_id", 0)
        )
        school_year_level_id = self.request.query_params.get("school_year_level_id")
        if school_year_level_id:
            qs = qs.filter(school_year_level_id=school_year_level_id)
        return qs

    def get_serializer_class(self):
        if self.action == "create":
            return SchoolFeeCreateSerializer
        if self.action in ("update", "partial_update"):
            return SchoolFeeUpdateSerializer
        return SchoolFeeSerializer

    def create(self, request, *args, **kwargs):
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

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = SchoolFeeUpdateSerializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        d = serializer.validated_data
        try:
            school_fee = SchoolFeeService.update(
                school_fee=instance,
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

    @action(detail=False, methods=["get"], url_path="summaries")
    def summaries(self, request):
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
