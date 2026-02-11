from rest_framework import serializers


class GradeItemSerializer(serializers.Serializer):
    enrollment_id = serializers.IntegerField()
    raw_score = serializers.DecimalField(max_digits=6, decimal_places=2, required=False, allow_null=True)
    is_absent = serializers.BooleanField(required=False, default=False)
    is_excused = serializers.BooleanField(required=False, default=False)
    remark = serializers.CharField(required=False, allow_blank=True)


class AssessmentGradesPreviewSerializer(serializers.Serializer):
    grades = serializers.ListField(child=GradeItemSerializer())


class AssessmentGradesCommitSerializer(serializers.Serializer):
    grades = serializers.ListField(child=GradeItemSerializer())
