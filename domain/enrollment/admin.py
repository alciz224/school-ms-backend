from django.contrib import admin

from domain.enrollment.models import Classroom, StudentEnrollment


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
    search_fields = ("annual_identifier", "first_name", "last_name", "student__email")
