from django.contrib import admin

from domain.enrollment.models import Classroom, StudentEnrollment, TeacherAssignment


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("id", "school_year_level", "name", "capacity", "is_active", "is_deleted")
    list_filter = ("school_year_level", "is_active", "is_deleted")
    search_fields = ("name",)


@admin.register(StudentEnrollment)
class StudentEnrollmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "student",
        "school_year_level",
        "classroom",
        "enrollment_status",
        "enrollment_date",
        "annual_identifier",
        "is_active",
        "is_deleted",
    )
    list_filter = ("enrollment_status", "school_year_level", "is_active", "is_deleted")
    search_fields = ("annual_identifier", "first_name", "last_name", "student__user__email")


@admin.register(TeacherAssignment)
class TeacherAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "school_year_teacher",
        "classroom",
        "school_year_level_subject",
        "assignment_status",
        "start_date",
        "end_date",
    )
    list_filter = ("assignment_status",)
    search_fields = (
        "school_year_teacher__teacher__user__email",
        "school_year_teacher__teacher__user__first_name",
        "school_year_teacher__teacher__user__last_name",
        "classroom__name",
    )
    autocomplete_fields = ("school_year_teacher", "classroom", "school_year_level_subject", "replaced_by")
