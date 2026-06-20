from rest_framework import serializers

from domain.assessment.models import Assessment, AssessmentSubject, StudentAssessment


class AssessmentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    cycle_name = serializers.CharField(source="school_year_cycle.cycle.name", read_only=True, default="")
    term_name = serializers.CharField(source="school_year_cycle_term.term.name", read_only=True, default="")
    type_name = serializers.CharField(source="assessment_type.name", read_only=True, default="")
    school_year_id = serializers.IntegerField(source="school_year.pk")
    school_year_cycle_id = serializers.IntegerField(source="school_year_cycle.pk")
    school_year_cycle_term_id = serializers.IntegerField(source="school_year_cycle_term.pk")
    assessment_type_id = serializers.IntegerField(source="assessment_type.pk")

    class Meta:
        model = Assessment
        fields = [
            "id",
            "school_year_id",
            "school_year_cycle_id",
            "school_year_cycle_term_id",
            "assessment_type_id",
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "cycle_name",
            "term_name",
            "type_name",
        ]

    def create(self, validated_data):
        validated_data.pop("school_year", None)
        validated_data.pop("school_year_cycle", None)
        validated_data.pop("school_year_cycle_term", None)
        validated_data.pop("assessment_type", None)
        return Assessment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("school_year", None)
        validated_data.pop("school_year_cycle", None)
        validated_data.pop("school_year_cycle_term", None)
        validated_data.pop("assessment_type", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class AssessmentDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    cycle_name = serializers.CharField(source="school_year_cycle.cycle.name", read_only=True, default="")
    term_name = serializers.CharField(source="school_year_cycle_term.term.name", read_only=True, default="")
    type_name = serializers.CharField(source="assessment_type.name", read_only=True, default="")
    school_year_name = serializers.CharField(source="school_year.name", read_only=True, default="")
    school_year_id = serializers.IntegerField(source="school_year.pk", read_only=True)
    school_year_cycle_id = serializers.IntegerField(source="school_year_cycle.pk", read_only=True)
    school_year_cycle_term_id = serializers.IntegerField(source="school_year_cycle_term.pk", read_only=True)
    assessment_type_id = serializers.IntegerField(source="assessment_type.pk", read_only=True)

    class Meta:
        model = Assessment
        fields = [
            "id",
            "school_year_id",
            "school_year_name",
            "school_year_cycle_id",
            "school_year_cycle_term_id",
            "assessment_type_id",
            "name",
            "description",
            "start_date",
            "end_date",
            "status",
            "cycle_name",
            "term_name",
            "type_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class AssessmentSubjectSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    subject_name = serializers.CharField(
        source="school_year_level_subject.subject.name", read_only=True, default=""
    )
    classroom_name = serializers.CharField(source="classroom.name", read_only=True, default="")
    teacher_name = serializers.SerializerMethodField()
    coefficient = serializers.DecimalField(
        source="school_year_level_subject.coefficient", read_only=True, max_digits=5, decimal_places=2, default=0
    )
    assessment_id = serializers.IntegerField(source="assessment.pk")
    classroom_id = serializers.IntegerField(source="classroom.pk")
    school_year_level_subject_id = serializers.IntegerField(source="school_year_level_subject.pk")
    teacher_assignment_id = serializers.IntegerField(source="teacher_assignment.pk")

    class Meta:
        model = AssessmentSubject
        fields = [
            "id",
            "assessment_id",
            "classroom_id",
            "school_year_level_subject_id",
            "teacher_assignment_id",
            "status",
            "max_score",
            "instructions",
            "subject_name",
            "classroom_name",
            "teacher_name",
            "coefficient",
        ]

    def get_teacher_name(self, obj):
        if obj.teacher_assignment and obj.teacher_assignment.school_year_teacher:
            t = obj.teacher_assignment.school_year_teacher.teacher
            return t.full_name
        return ""


class AssessmentSubjectDetailSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    subject_name = serializers.CharField(
        source="school_year_level_subject.subject.name", read_only=True, default=""
    )
    classroom_name = serializers.CharField(source="classroom.name", read_only=True, default="")
    level_name = serializers.CharField(
        source="school_year_level_subject.school_year_level.level.name", read_only=True, default=""
    )
    track_name = serializers.CharField(
        source="school_year_level_subject.school_year_level.track.name", read_only=True, default=""
    )
    teacher_name = serializers.SerializerMethodField()
    coefficient = serializers.DecimalField(
        source="school_year_level_subject.coefficient", read_only=True, max_digits=5, decimal_places=2, default=0
    )
    assessment_id = serializers.IntegerField(source="assessment.pk", read_only=True)
    classroom_id = serializers.IntegerField(source="classroom.pk", read_only=True)
    school_year_level_subject_id = serializers.IntegerField(source="school_year_level_subject.pk", read_only=True)
    teacher_assignment_id = serializers.IntegerField(source="teacher_assignment.pk", read_only=True)

    class Meta:
        model = AssessmentSubject
        fields = [
            "id",
            "assessment_id",
            "classroom_id",
            "school_year_level_subject_id",
            "teacher_assignment_id",
            "status",
            "max_score",
            "instructions",
            "subject_name",
            "classroom_name",
            "level_name",
            "track_name",
            "teacher_name",
            "coefficient",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_teacher_name(self, obj):
        if obj.teacher_assignment and obj.teacher_assignment.school_year_teacher:
            t = obj.teacher_assignment.school_year_teacher.teacher
            return t.full_name
        return ""


class StudentAssessmentSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    assessment_subject_id = serializers.IntegerField(source="assessment_subject.pk")
    student_enrollment_id = serializers.IntegerField(source="student_enrollment.pk")

    class Meta:
        model = StudentAssessment
        fields = [
            "id",
            "assessment_subject_id",
            "student_enrollment_id",
            "raw_score",
            "status",
            "is_absent",
            "is_excused",
            "remark",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        validated_data.pop("assessment_subject", None)
        validated_data.pop("student_enrollment", None)
        return StudentAssessment.objects.create(**validated_data)

    def update(self, instance, validated_data):
        validated_data.pop("assessment_subject", None)
        validated_data.pop("student_enrollment", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class StudentGradeSerializer(serializers.ModelSerializer):
    id = serializers.CharField(read_only=True)
    student_name = serializers.SerializerMethodField()
    student_last_name = serializers.SerializerMethodField()
    student_first_name = serializers.SerializerMethodField()
    student_matricule = serializers.SerializerMethodField()
    subject_name = serializers.SerializerMethodField()
    normalized_score = serializers.SerializerMethodField()
    assessment_subject_id = serializers.IntegerField(source="assessment_subject.pk", read_only=True)
    student_enrollment_id = serializers.IntegerField(source="student_enrollment.pk", read_only=True)
    max_score = serializers.DecimalField(
        source="assessment_subject.max_score", read_only=True, max_digits=6, decimal_places=2, default=0
    )

    class Meta:
        model = StudentAssessment
        fields = [
            "id",
            "assessment_subject_id",
            "student_enrollment_id",
            "raw_score",
            "normalized_score",
            "status",
            "is_absent",
            "is_excused",
            "remark",
            "student_name",
            "student_last_name",
            "student_first_name",
            "student_matricule",
            "subject_name",
            "max_score",
        ]

    def get_student_name(self, obj):
        if obj.student_enrollment:
            return obj.student_enrollment.display_name
        return ""

    def get_student_last_name(self, obj):
        if obj.student_enrollment:
            return obj.student_enrollment.last_name
        return ""

    def get_student_first_name(self, obj):
        if obj.student_enrollment:
            return obj.student_enrollment.first_name
        return ""

    def get_student_matricule(self, obj):
        if obj.student_enrollment:
            return obj.student_enrollment.annual_identifier
        return ""

    def get_subject_name(self, obj):
        if obj.assessment_subject and obj.assessment_subject.school_year_level_subject:
            return obj.assessment_subject.school_year_level_subject.subject.name
        return ""

    def get_normalized_score(self, obj):
        if obj.raw_score is not None and obj.assessment_subject and obj.assessment_subject.max_score:
            try:
                return round(float(obj.raw_score) / float(obj.assessment_subject.max_score) * 20, 2)
            except (ValueError, ZeroDivisionError):
                return None
        return None
