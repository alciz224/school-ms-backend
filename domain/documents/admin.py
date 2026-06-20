from django.contrib import admin

from domain.documents.models import DocumentRequest


@admin.register(DocumentRequest)
class DocumentRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "document_type",
        "student_enrollment",
        "school_year_cycle_term",
        "status",
        "generated_at",
        "file_size",
    )
    list_filter = ("document_type", "status", "school_year_cycle_term")
    search_fields = (
        "student_enrollment__annual_identifier",
        "student_enrollment__first_name",
        "student_enrollment__last_name",
        "student_enrollment__student__user__email",
        "file_hash",
    )
    autocomplete_fields = ("student_enrollment", "school_year_cycle_term")
    readonly_fields = (
        "file_hash",
        "file_size",
        "generated_file",
        "generated_at",
        "created_at",
        "updated_at",
    )
    ordering = ("-created_at",)
