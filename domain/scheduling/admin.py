"""Admin configuration for scheduling domain."""

from django.contrib import admin

from domain.scheduling.models import Schedule


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    """Admin interface for Schedule model."""
    
    list_display = [
        "id",
        "classroom",
        "day_of_week",
        "time_slot",
        "subject_name",
        "teacher_name",
        "effective_from",
        "effective_to",
        "status",
    ]
    list_filter = [
        "status",
        "day_of_week",
        "school_year",
        "school_year_cycle",
    ]
    search_fields = [
        "classroom__name",
        "teacher_assignment__school_year_teacher__teacher__first_name",
        "teacher_assignment__school_year_teacher__teacher__last_name",
        "teacher_assignment__school_year_level_subject__subject__name",
    ]
    readonly_fields = ["created_at", "updated_at"]
    
    fieldsets = (
        ("Basic Information", {
            "fields": ("school_year", "school_year_cycle", "classroom", "teacher_assignment")
        }),
        ("Scheduling", {
            "fields": ("day_of_week", "time_slot")
        }),
        ("Validity Period", {
            "fields": ("effective_from", "effective_to")
        }),
        ("Status", {
            "fields": ("status", "is_deleted")
        }),
        ("Metadata", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )
    
    def subject_name(self, obj):
        """Display subject name."""
        return obj.subject.name
    subject_name.short_description = "Subject"
    
    def teacher_name(self, obj):
        """Display teacher name."""
        teacher = obj.teacher
        return f"{teacher.first_name} {teacher.last_name}"
    teacher_name.short_description = "Teacher"
