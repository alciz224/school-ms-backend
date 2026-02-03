"""Django admin configuration for Academic domain."""
from django.contrib import admin
from django.utils.html import format_html

from domain.academic.models import (
    AcademicYear,
    AssessmentType,
    Cycle,
    Level,
    Subject,
    Term,
    TermType,
    Track,
)
from domain.academic.services import AcademicYearService


@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):
    """Admin interface for AcademicYear model."""

    list_display = [
        "code",
        "start_year",
        "end_year",
        "is_current_badge",
        "status_badge",
        "created_at",
    ]
    list_filter = ["status", "is_current", "start_year"]
    search_fields = ["code"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["-start_year"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("code", "start_year", "end_year"),
            },
        ),
        (
            "Status",
            {
                "fields": ("status", "is_current"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(ordering="is_current", description="Current")
    def is_current_badge(self, obj):
        """Display current status as badge."""
        if obj.is_current:
            return format_html(
                '<span style="background-color: {}; color: white; '
                'padding: 3px 10px; border-radius: 3px;">{}</span>',
                '#28a745', 'Current'
            )
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            '#6c757d', 'Not Current'
        )

    @admin.display(ordering="status", description="Status")
    def status_badge(self, obj):
        """Display status as colored badge."""
        colors = {
            "DRAFT": "#ffc107",
            "ACTIVE": "#28a745",
            "ARCHIVED": "#6c757d",
        }
        color = colors.get(obj.status, "#6c757d")
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, obj.get_status_display()
        )

    actions = ["activate_years", "archive_years"]

    def activate_years(self, request, queryset):
        """Activate selected academic years."""
        count = 0
        for year in queryset:
            try:
                AcademicYearService.activate(academic_year=year, user=request.user)
                count += 1
            except Exception as e:
                self.message_user(request, f"Error activating {year}: {e}", level="error")
        
        self.message_user(request, f"Successfully activated {count} academic year(s).")

    activate_years.short_description = "Activate selected years"

    def archive_years(self, request, queryset):
        """Archive selected academic years."""
        count = 0
        for year in queryset:
            try:
                AcademicYearService.archive(academic_year=year, user=request.user)
                count += 1
            except Exception as e:
                self.message_user(request, f"Error archiving {year}: {e}", level="error")
        
        self.message_user(request, f"Successfully archived {count} academic year(s).")

    archive_years.short_description = "Archive selected years"


@admin.register(Cycle)
class CycleAdmin(admin.ModelAdmin):
    """Admin interface for Cycle model."""

    list_display = ["code", "name", "has_track_badge", "created_at"]
    list_filter = ["has_track"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["code"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("code", "name", "has_track"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(ordering="has_track", description="Has Tracks")
    def has_track_badge(self, obj):
        """Display has_track as badge."""
        if obj.has_track:
            return format_html(
                '<span style="background-color: {}; color: white; '
                'padding: 3px 10px; border-radius: 3px;">{}</span>',
                '#17a2b8', 'Yes'
            )
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px;">{}</span>',
            '#6c757d', 'No'
        )


@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    """Admin interface for Track model."""

    list_display = ["code", "name", "cycle", "created_at"]
    list_filter = ["cycle"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["cycle", "code"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("code", "name", "cycle"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    """Admin interface for Level model."""

    list_display = ["code", "name", "cycle", "track", "order", "created_at"]
    list_filter = ["cycle", "track"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["cycle", "order"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("code", "name", "cycle", "track", "order"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    """Admin interface for Subject model."""

    list_display = ["code", "name", "created_at"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["name"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("code", "name", "description"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(AssessmentType)
class AssessmentTypeAdmin(admin.ModelAdmin):
    """Admin interface for AssessmentType model."""

    list_display = ["code", "name", "created_at"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["name"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("code", "name", "description"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(TermType)
class TermTypeAdmin(admin.ModelAdmin):
    """Admin interface for TermType model."""

    list_display = ["code", "name", "period_count", "created_at"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["period_count", "name"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("code", "name", "period_count"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    """Admin interface for Term model."""

    list_display = ["code", "name", "term_type", "order", "created_at"]
    list_filter = ["term_type"]
    search_fields = ["code", "name"]
    readonly_fields = ["created_at", "updated_at", "created_by", "updated_by"]
    ordering = ["term_type", "order"]

    fieldsets = (
        (
            "Basic Information",
            {
                "fields": ("term_type", "code", "name", "order"),
            },
        ),
        (
            "Audit",
            {
                "fields": ("created_at", "updated_at", "created_by", "updated_by"),
                "classes": ("collapse",),
            },
        ),
    )
