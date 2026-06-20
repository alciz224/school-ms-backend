from django.contrib import admin

from domain.assessment.models import (
    Assessment,
    AssessmentSubject,
    ReportCard,
    ReportCardSubject,
    StudentAssessment,
    Transcript,
)


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "school_year",
        "school_year_cycle",
        "school_year_cycle_term",
        "assessment_type",
        "status",
        "start_date",
        "end_date",
    )
    list_filter = ("status", "assessment_type", "school_year")
    search_fields = ("name", "school_year__name", "assessment_type__name")
    autocomplete_fields = ("school_year", "school_year_cycle", "school_year_cycle_term", "assessment_type")
    ordering = ("-start_date",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(AssessmentSubject)
class AssessmentSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment",
        "classroom",
        "school_year_level_subject",
        "teacher_assignment",
        "status",
        "max_score",
        "is_active",
    )
    list_filter = ("status", "is_active")
    search_fields = (
        "assessment__name",
        "classroom__name",
        "school_year_level_subject__subject__name",
        "teacher_assignment__school_year_teacher__teacher__user__first_name",
        "teacher_assignment__school_year_teacher__teacher__user__last_name",
    )
    autocomplete_fields = ("assessment", "classroom", "school_year_level_subject", "teacher_assignment")
    ordering = ("assessment", "classroom")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReportCard)
class ReportCardAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student_enrollment",
        "school_year_cycle_term",
        "overall_average",
        "rank",
        "is_final",
        "is_active",
    )
    list_filter = ("is_final", "is_active", "school_year_cycle_term__school_year_cycle__school_year")
    search_fields = (
        "student_enrollment__student__user__email",
        "student_enrollment__student__user__first_name",
        "student_enrollment__student__user__last_name",
    )
    autocomplete_fields = ("student_enrollment", "school_year_cycle_term")
    ordering = ("school_year_cycle_term", "student_enrollment")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ReportCardSubject)
class ReportCardSubjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "report_card",
        "school_year_level_subject",
        "average",
        "coefficient",
        "is_active",
    )
    list_filter = ("is_active",)
    search_fields = (
        "report_card__student_enrollment__student__user__email",
        "school_year_level_subject__subject__name",
    )
    autocomplete_fields = ("report_card", "school_year_level_subject")
    ordering = ("report_card", "school_year_level_subject")
    readonly_fields = ("created_at", "updated_at")


@admin.register(StudentAssessment)
class StudentAssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "assessment_subject",
        "student_enrollment",
        "raw_score",
        "is_absent",
        "is_excused",
        "status",
        "is_active",
    )
    list_filter = ("status", "is_absent", "is_excused", "is_active")
    search_fields = (
        "student_enrollment__student__user__email",
        "student_enrollment__student__user__first_name",
        "student_enrollment__student__user__last_name",
        "assessment_subject__subject__name",
    )
    autocomplete_fields = ("assessment_subject", "student_enrollment")
    ordering = ("-assessment_subject__assessment__start_date", "student_enrollment")


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student_enrollment",
        "school_year",
        "overall_average",
        "decision",
        "is_active",
    )
    list_filter = ("is_active", "school_year")
    search_fields = (
        "student_enrollment__student__user__email",
        "student_enrollment__student__user__first_name",
        "student_enrollment__student__user__last_name",
    )
    autocomplete_fields = ("student_enrollment", "school_year")
    ordering = ("-school_year__start_date", "student_enrollment")
    readonly_fields = ("created_at", "updated_at")
