from rest_framework import serializers

from domain.finance.models import SchoolFee


class SchoolFeeSerializer(serializers.ModelSerializer):
    fee_name = serializers.CharField(source="fee_type.name", read_only=True)
    level_name = serializers.CharField(source="school_year_level.level.name", read_only=True, default="")

    class Meta:
        model = SchoolFee
        fields = [
            "id",
            "school_year",
            "school_year_level",
            "fee_type",
            "fee_name",
            "level_name",
            "amount",
            "due_date",
            "school_year_cycle",
            "is_mandatory",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_school_year(self, value):
        return value.pk

    def validate_school_year_level(self, value):
        return value.pk

    def validate_fee_type(self, value):
        return value.pk

    def validate_school_year_cycle(self, value):
        if value:
            return value.pk
        return None


class SchoolFeeCreateSerializer(serializers.Serializer):
    school_year_id = serializers.IntegerField()
    school_year_level_id = serializers.IntegerField()
    fee_type_id = serializers.IntegerField()
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    due_date = serializers.DateField()
    school_year_cycle_id = serializers.IntegerField(required=False, allow_null=True)
    is_mandatory = serializers.BooleanField(default=True)


class SchoolFeeUpdateSerializer(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=False)
    due_date = serializers.DateField(required=False)
    is_mandatory = serializers.BooleanField(required=False)
