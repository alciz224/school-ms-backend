from rest_framework import serializers

from domain.assessment.models import ReportCard, ReportCardSubject, Transcript


class ReportCardSubjectSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="school_year_level_subject.subject.name", read_only=True)

    class Meta:
        model = ReportCardSubject
        fields = [
            "id",
            "school_year_level_subject",
            "subject_name",
            "average",
            "coefficient",
            "teacher_name",
            "remark",
        ]
        read_only_fields = fields


class ReportCardSerializer(serializers.ModelSerializer):
    subjects = ReportCardSubjectSerializer(many=True, read_only=True)

    class Meta:
        model = ReportCard
        fields = [
            "id",
            "student_enrollment",
            "school_year_cycle_term",
            "classroom",
            "overall_average",
            "rank",
            "decision",
            "is_final",
            "generated_at",
            "raw_data",
            "subjects",
        ]
        read_only_fields = fields


class ReportCardGenerateSerializer(serializers.Serializer):
    classroom_id = serializers.IntegerField()
    term_id = serializers.IntegerField()
    force = serializers.BooleanField(required=False, default=False)


class TranscriptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transcript
        fields = [
            "id",
            "student_enrollment",
            "school_year",
            "overall_average",
            "decision",
            "generated_at",
            "raw_data",
        ]
        read_only_fields = fields


class TranscriptGenerateSerializer(serializers.Serializer):
    student_enrollment_id = serializers.IntegerField()
    school_year_id = serializers.IntegerField()
