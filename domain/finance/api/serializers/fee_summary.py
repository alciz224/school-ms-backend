from rest_framework import serializers


class FeeSummarySerializer(serializers.Serializer):
    student_id = serializers.CharField()
    student_name = serializers.CharField()
    class_name = serializers.CharField()
    level = serializers.CharField()
    total_due = serializers.FloatField()
    total_paid = serializers.FloatField()
    balance = serializers.FloatField()
    status = serializers.CharField()
    last_payment_date = serializers.DateField(allow_null=True)


class FinanceStatsSerializer(serializers.Serializer):
    total_expected = serializers.FloatField()
    total_collected = serializers.FloatField()
    total_pending = serializers.FloatField()
    total_overdue = serializers.FloatField()
    collection_rate = serializers.FloatField()
    students_count = serializers.IntegerField()
    students_paid = serializers.IntegerField()
    students_pending = serializers.IntegerField()
