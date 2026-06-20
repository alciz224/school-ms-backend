from rest_framework import serializers

from domain.finance.models import StudentPayment


class StudentPaymentSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student_enrollment.student.full_name", read_only=True, default="")
    fee_name = serializers.CharField(source="school_fee.fee_type.name", read_only=True, default="")

    class Meta:
        model = StudentPayment
        fields = [
            "id",
            "student_enrollment",
            "school_fee",
            "student_name",
            "fee_name",
            "amount_paid",
            "payment_date",
            "payment_method",
            "reference_number",
            "collected_by",
            "notes",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class StudentPaymentCreateSerializer(serializers.Serializer):
    student_enrollment_id = serializers.IntegerField()
    school_fee_id = serializers.IntegerField()
    amount_paid = serializers.DecimalField(max_digits=10, decimal_places=2)
    payment_date = serializers.DateField()
    payment_method = serializers.ChoiceField(choices=[
        "CASH", "BANK_TRANSFER", "MOBILE_MONEY", "CHECK"
    ])
    reference_number = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    collected_by = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    notes = serializers.CharField(required=False, allow_null=True, allow_blank=True)
