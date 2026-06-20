"""
Admin configuration for account models.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import (
    AdminProfile,
    CustomUser,
    LoginAttempt,
    ParentChild,
    ParentProfile,
    PhoneHistory,
    SchoolAdminAssignment,
    SchoolAdminProfile,
    SecurityQuestion,
    SecurityQuestionAttempt,
    StudentProfile,
    SuperAdminProfile,
    TeacherProfile,
    VerificationCode,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin configuration for CustomUser."""

    list_display = (
        "identifier",
        "first_name",
        "last_name",
        "is_verified",
        "is_active",
        "is_staff",
        "date_joined",
    )
    list_filter = (
        "is_active",
        "is_staff",
        "is_superuser",
        "email_verified",
        "phone_verified",
        "date_joined",
    )
    search_fields = ("email", "phone", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("email", "phone", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Verification"),
            {
                "fields": (
                    "email_verified",
                    "email_verified_at",
                    "phone_verified",
                    "phone_verified_at",
                )
            },
        ),
        (
            _("Backup contact"),
            {"fields": ("backup_phone", "backup_phone_owner")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "phone",
                    "first_name",
                    "last_name",
                    "password1",
                    "password2",
                ),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login", "email_verified_at", "phone_verified_at")

    def identifier(self, obj):
        """Display the user's identifier."""
        return obj.identifier

    identifier.short_description = _("Identifier")

    def is_verified(self, obj):
        """Display verification status."""
        return obj.is_verified

    is_verified.boolean = True
    is_verified.short_description = _("Verified")


@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(admin.ModelAdmin):
    """Admin configuration for SecurityQuestion."""

    list_display = ("user", "question", "order", "created_at", "updated_at")
    list_filter = ("order", "created_at")
    search_fields = ("user__email", "user__phone", "question")
    ordering = ("user", "order")
    readonly_fields = ("answer_hash", "created_at", "updated_at")


@admin.register(SecurityQuestionAttempt)
class SecurityQuestionAttemptAdmin(admin.ModelAdmin):
    """Admin configuration for SecurityQuestionAttempt."""

    list_display = (
        "user",
        "ip_address",
        "questions_answered",
        "correct_answers",
        "success",
        "created_at",
    )
    list_filter = ("success", "created_at")
    search_fields = ("user__email", "user__phone", "ip_address")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


@admin.register(ParentChild)
class ParentChildAdmin(admin.ModelAdmin):
    list_display = ("parent", "child", "relationship_type", "is_primary", "is_active")
    list_filter = ("relationship_type", "is_primary", "is_active")
    search_fields = (
        "parent__user__email",
        "parent__user__first_name",
        "parent__user__last_name",
        "child__user__email",
        "child__user__first_name",
        "child__user__last_name",
    )
    autocomplete_fields = ("parent", "child")
    ordering = ("child", "parent")


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """Admin configuration for VerificationCode."""

    list_display = (
        "user",
        "type",
        "purpose",
        "code",
        "is_used",
        "expires_at",
        "attempts",
        "created_at",
    )
    list_filter = ("type", "purpose", "is_used", "created_at")
    search_fields = ("user__email", "user__phone", "code")
    ordering = ("-created_at",)
    readonly_fields = ("code", "created_at")


@admin.register(PhoneHistory)
class PhoneHistoryAdmin(admin.ModelAdmin):
    """Admin configuration for PhoneHistory."""

    list_display = ("user", "phone", "verified", "reason", "added_at", "removed_at")
    list_filter = ("verified", "reason", "removed_at")
    search_fields = ("user__email", "user__phone", "phone")
    ordering = ("-removed_at",)
    readonly_fields = ("added_at", "removed_at")


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin configuration for LoginAttempt."""

    list_display = (
        "identifier",
        "user",
        "ip_address",
        "success",
        "failure_reason",
        "created_at",
    )
    list_filter = ("success", "failure_reason", "created_at")
    search_fields = ("identifier", "ip_address", "user__email", "user__phone")
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)


# ==========================================================================
# PROFILES (un par rôle / portail)
# ==========================================================================


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "date_of_birth",
        "gender",
        "nationality",
        "birth_cert_number",
        "has_disability",
        "is_active",
    )
    list_filter = ("gender", "nationality", "has_disability", "is_active")
    search_fields = (
        "user__first_name",
        "user__last_name",
        "user__email",
        "user__phone",
        "birth_cert_number",
    )
    autocomplete_fields = ("user", "place_of_birth")
    ordering = ("user__last_name", "user__first_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "user",
        "employee_id",
        "diploma",
        "employment_type",
        "gender",
        "is_active",
    )
    list_filter = ("diploma", "employment_type", "gender", "is_active")
    search_fields = (
        "employee_id",
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
    )
    autocomplete_fields = ("user",)
    ordering = ("user__last_name", "user__first_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(ParentProfile)
class ParentProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "gender", "occupation", "locality", "is_active")
    list_filter = ("gender", "is_active")
    search_fields = (
        "user__email",
        "user__phone",
        "user__first_name",
        "user__last_name",
        "occupation",
    )
    autocomplete_fields = ("user", "locality")
    ordering = ("user__last_name", "user__first_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "position", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__email", "user__first_name", "user__last_name", "position")
    autocomplete_fields = ("user",)
    ordering = ("user__last_name", "user__first_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SchoolAdminProfile)
class SchoolAdminProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "user", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
    autocomplete_fields = ("user",)
    ordering = ("user__last_name", "user__first_name")
    readonly_fields = ("created_at", "updated_at")


@admin.register(SchoolAdminAssignment)
class SchoolAdminAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "school_admin",
        "school",
        "position",
        "start_date",
        "end_date",
        "is_primary",
        "is_active",
    )
    list_filter = ("position", "is_primary", "is_active", "school")
    search_fields = (
        "school_admin__user__email",
        "school_admin__user__first_name",
        "school_admin__user__last_name",
        "school__name",
        "school__code",
    )
    autocomplete_fields = ("school_admin", "school")
    ordering = ("-start_date",)
    readonly_fields = ("created_at", "updated_at")


@admin.register(SuperAdminProfile)
class SuperAdminProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "is_active")
    list_filter = ("is_active",)
    search_fields = ("user__email", "user__first_name", "user__last_name", "department")
    autocomplete_fields = ("user",)
    ordering = ("user__last_name", "user__first_name")
    readonly_fields = ("created_at", "updated_at")
