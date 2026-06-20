from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from domain.enrollment.api.permissions import IsSchoolStaffOrAdmin
from domain.assessment.models import ReportCard, Transcript

from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


class ReportCardListSerializer(serializers.Serializer):
    id = serializers.CharField()
    student_enrollment_id = serializers.CharField()
    school_year_cycle_term_id = serializers.CharField()
    school_year_id = serializers.CharField()
    classroom_id = serializers.CharField()
    overall_average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    rank = serializers.IntegerField(allow_null=True)
    decision = serializers.CharField()
    status = serializers.SerializerMethodField()
    generated_at = serializers.DateTimeField()
    locked_at = serializers.DateTimeField(allow_null=True)
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    classroom_name = serializers.SerializerMethodField()

    def get_status(self, obj):
        return "FINAL" if obj.is_final else "DRAFT"

    def get_student_name(self, obj):
        return obj.student_enrollment.display_name if obj.student_enrollment else ""

    def get_student_matricule(self, obj):
        return obj.student_enrollment.annual_identifier if obj.student_enrollment else ""

    def get_term_name(self, obj):
        if obj.school_year_cycle_term:
            return obj.school_year_cycle_term.term.name if obj.school_year_cycle_term.term else ""
        return ""

    def get_classroom_name(self, obj):
        return obj.classroom.name if obj.classroom else ""


class ReportCardDetailSerializer(serializers.Serializer):
    id = serializers.CharField()
    student_enrollment_id = serializers.CharField()
    school_year_cycle_term_id = serializers.CharField()
    school_year_id = serializers.CharField()
    classroom_id = serializers.CharField()
    overall_average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    rank = serializers.IntegerField(allow_null=True)
    decision = serializers.CharField()
    status = serializers.SerializerMethodField()
    generated_at = serializers.DateTimeField()
    locked_at = serializers.DateTimeField(allow_null=True)
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    term_name = serializers.SerializerMethodField()
    classroom_name = serializers.SerializerMethodField()

    def get_status(self, obj):
        return "FINAL" if obj.is_final else "DRAFT"

    def get_student_name(self, obj):
        return obj.student_enrollment.display_name if obj.student_enrollment else ""

    def get_student_matricule(self, obj):
        return obj.student_enrollment.annual_identifier if obj.student_enrollment else ""

    def get_term_name(self, obj):
        if obj.school_year_cycle_term:
            return obj.school_year_cycle_term.term.name if obj.school_year_cycle_term.term else ""
        return ""

    def get_classroom_name(self, obj):
        return obj.classroom.name if obj.classroom else ""


class ReportCardCreateSerializer(serializers.Serializer):
    student_enrollment_id = serializers.CharField()
    school_year_cycle_term_id = serializers.CharField()
    classroom_id = serializers.CharField()
    overall_average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    rank = serializers.IntegerField(allow_null=True, required=False)
    decision = serializers.CharField(required=False, allow_blank=True)


class ReportCardUpdateSerializer(serializers.Serializer):
    overall_average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    rank = serializers.IntegerField(allow_null=True, required=False)
    decision = serializers.CharField(required=False, allow_blank=True)
    is_final = serializers.BooleanField(required=False)


class ReportCardListView(APIView):
    """
    List report cards.
    GET /report-cards/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("student_enrollment_id", OpenApiTypes.STR, required=False),
            OpenApiParameter("school_year_id", OpenApiTypes.STR, required=False),
            OpenApiParameter("status", OpenApiTypes.STR, required=False),
        ],
        responses=ReportCardListSerializer(many=True),
    )
    def get(self, request):
        qs = ReportCard.objects.filter(is_deleted=False).select_related(
            "student_enrollment", "school_year_cycle_term__term", "classroom"
        )
        student_enrollment_id = request.query_params.get("student_enrollment_id")
        school_year_id = request.query_params.get("school_year_id")
        status_param = request.query_params.get("status")
        if student_enrollment_id:
            qs = qs.filter(student_enrollment_id=student_enrollment_id)
        if school_year_id:
            qs = qs.filter(
                student_enrollment__school_year_level__school_year_cycle__school_year_id=school_year_id
            )
        if status_param:
            if status_param.upper() == "FINAL":
                qs = qs.filter(is_final=True)
            elif status_param.upper() == "DRAFT":
                qs = qs.filter(is_final=False)
        serializer = ReportCardListSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})

    @extend_schema(
        request=ReportCardCreateSerializer,
        responses=ReportCardDetailSerializer,
    )
    def post(self, request):
        serializer = ReportCardCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        rc = ReportCard.objects.create(
            student_enrollment_id=serializer.validated_data["student_enrollment_id"],
            school_year_cycle_term_id=serializer.validated_data["school_year_cycle_term_id"],
            classroom_id=serializer.validated_data["classroom_id"],
            overall_average=serializer.validated_data.get("overall_average"),
            rank=serializer.validated_data.get("rank"),
            decision=serializer.validated_data.get("decision", ""),
            created_by=request.user,
            updated_by=request.user,
        )
        output = ReportCardDetailSerializer(rc)
        return Response({"success": True, "data": output.data}, status=status.HTTP_201_CREATED)


class ReportCardDetailView(APIView):
    """
    Get/update a report card.
    GET/PATCH /report-cards/{id}/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=ReportCardDetailSerializer)
    def get(self, request, pk):
        try:
            rc = ReportCard.objects.select_related(
                "student_enrollment", "school_year_cycle_term__term", "classroom"
            ).get(id=pk, is_deleted=False)
        except ReportCard.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Report card not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ReportCardDetailSerializer(rc)
        return Response({"success": True, "data": serializer.data})

    @extend_schema(
        request=ReportCardUpdateSerializer,
        responses=ReportCardDetailSerializer,
    )
    def patch(self, request, pk):
        try:
            rc = ReportCard.objects.get(id=pk, is_deleted=False)
        except ReportCard.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Report card not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = ReportCardUpdateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        for attr, value in serializer.validated_data.items():
            setattr(rc, attr, value)
        rc.updated_by = request.user
        rc.save()
        output = ReportCardDetailSerializer(rc)
        return Response({"success": True, "data": output.data})


class TranscriptListSerializer(serializers.Serializer):
    id = serializers.CharField()
    student_enrollment_id = serializers.CharField()
    school_year_id = serializers.CharField()
    overall_average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    decision = serializers.CharField()
    status = serializers.CharField(default="FINAL")
    generated_at = serializers.DateTimeField()
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    school_year_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student_enrollment.display_name if obj.student_enrollment else ""

    def get_student_matricule(self, obj):
        return obj.student_enrollment.annual_identifier if obj.student_enrollment else ""

    def get_school_year_name(self, obj):
        return obj.school_year.name if obj.school_year else ""


class TranscriptDetailSerializer(serializers.Serializer):
    id = serializers.CharField()
    student_enrollment_id = serializers.CharField()
    school_year_id = serializers.CharField()
    overall_average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True)
    decision = serializers.CharField()
    status = serializers.CharField(default="FINAL")
    generated_at = serializers.DateTimeField()
    locked_at = serializers.DateTimeField(allow_null=True)
    student_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    school_year_name = serializers.SerializerMethodField()
    cycle_name = serializers.SerializerMethodField()
    level_name = serializers.SerializerMethodField()

    def get_student_name(self, obj):
        return obj.student_enrollment.display_name if obj.student_enrollment else ""

    def get_student_matricule(self, obj):
        return obj.student_enrollment.annual_identifier if obj.student_enrollment else ""

    def get_school_year_name(self, obj):
        return obj.school_year.name if obj.school_year else ""

    def get_cycle_name(self, obj):
        if obj.student_enrollment:
            syl = obj.student_enrollment.school_year_level
            if syl and syl.school_year_cycle:
                return syl.school_year_cycle.cycle.name if syl.school_year_cycle.cycle else ""
        return ""

    def get_level_name(self, obj):
        if obj.student_enrollment:
            syl = obj.student_enrollment.school_year_level
            if syl:
                return syl.level.name if syl.level else ""
        return ""


class TranscriptCreateSerializer(serializers.Serializer):
    student_enrollment_id = serializers.CharField()
    school_year_id = serializers.CharField()
    overall_average = serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False)
    decision = serializers.CharField(required=False, allow_blank=True)


class TranscriptListView(APIView):
    """
    List transcripts.
    GET /transcripts/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(
        parameters=[
            OpenApiParameter("student_enrollment_id", OpenApiTypes.STR, required=False),
            OpenApiParameter("school_year_id", OpenApiTypes.STR, required=False),
            OpenApiParameter("status", OpenApiTypes.STR, required=False),
        ],
        responses=TranscriptListSerializer(many=True),
    )
    def get(self, request):
        qs = Transcript.objects.filter(is_deleted=False).select_related(
            "student_enrollment", "school_year"
        )
        student_enrollment_id = request.query_params.get("student_enrollment_id")
        school_year_id = request.query_params.get("school_year_id")
        if student_enrollment_id:
            qs = qs.filter(student_enrollment_id=student_enrollment_id)
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        serializer = TranscriptListSerializer(qs, many=True)
        return Response({"success": True, "data": serializer.data})

    @extend_schema(
        request=TranscriptCreateSerializer,
        responses=TranscriptDetailSerializer,
    )
    def post(self, request):
        serializer = TranscriptCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        t = Transcript.objects.create(
            student_enrollment_id=serializer.validated_data["student_enrollment_id"],
            school_year_id=serializer.validated_data["school_year_id"],
            overall_average=serializer.validated_data.get("overall_average"),
            decision=serializer.validated_data.get("decision", ""),
        )
        output = TranscriptDetailSerializer(t)
        return Response({"success": True, "data": output.data}, status=status.HTTP_201_CREATED)


class TranscriptDetailView(APIView):
    """
    Get/update a transcript.
    GET/PATCH /transcripts/{id}/
    """
    permission_classes = [IsSchoolStaffOrAdmin]

    @extend_schema(responses=TranscriptDetailSerializer)
    def get(self, request, pk):
        try:
            t = Transcript.objects.select_related(
                "student_enrollment__school_year_level__school_year_cycle__cycle",
                "student_enrollment__school_year_level__level",
                "school_year",
            ).get(id=pk, is_deleted=False)
        except Transcript.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Transcript not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TranscriptDetailSerializer(t)
        return Response({"success": True, "data": serializer.data})

    @extend_schema(
        request=inline_serializer(
            name="TranscriptUpdate",
            fields={
                "overall_average": serializers.DecimalField(max_digits=6, decimal_places=2, allow_null=True, required=False),
                "decision": serializers.CharField(required=False),
            },
        ),
        responses=TranscriptDetailSerializer,
    )
    def patch(self, request, pk):
        try:
            t = Transcript.objects.get(id=pk, is_deleted=False)
        except Transcript.DoesNotExist:
            return Response(
                {"success": False, "error": {"code": "not_found", "message": "Transcript not found"}},
                status=status.HTTP_404_NOT_FOUND,
            )
        for attr in ["overall_average", "decision"]:
            if attr in request.data:
                setattr(t, attr, request.data[attr])
        t.save()
        output = TranscriptDetailSerializer(t)
        return Response({"success": True, "data": output.data})
