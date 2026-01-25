# domain/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import (
    CustomUser,
    SecurityQuestion,
    VerificationCode,
    PhoneHistory,
    LoginAttempt,
)


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """Admin amélioré pour CustomUser."""

    list_display = [
        "identifier_display",
        "full_name",
        "verification_badge",
        "security_badge",
        "is_active",
        "date_joined",
    ]

    list_filter = [
        "is_active",
        "is_staff",
        "email_verified",
        "phone_verified",
        "date_joined",
    ]

    search_fields = ["email", "phone", "first_name", "last_name"]
    ordering = ["-date_joined"]

    readonly_fields = [
        "id",
        "date_joined",
        "last_login",
        "security_score_display",
        "verification_status_display",
    ]

    fieldsets = (
        (None, {"fields": ("id", "password")}),
        (_("Identifiants"), {"fields": ("email", "phone")}),
        (_("Informations personnelles"), {"fields": ("first_name", "last_name")}),
        (
            _("Vérification"),
            {
                "fields": (
                    "verification_status_display",
                    "email_verified",
                    "phone_verified",
                )
            },
        ),
        (
            _("Sécurité"),
            {
                "fields": (
                    "security_score_display",
                    "backup_phone",
                    "backup_phone_owner",
                )
            },
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
                "classes": ("collapse",),
            },
        ),
        (
            _("Dates"),
            {"fields": ("date_joined", "last_login"), "classes": ("collapse",)},
        ),
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

    def identifier_display(self, obj):
        return obj.email or obj.phone

    identifier_display.short_description = _("Identifiant")

    def verification_badge(self, obj):
        if obj.email_verified and obj.phone_verified:
            return format_html('<span style="color: #28a745;">●●</span> Complet')
        elif obj.email_verified or obj.phone_verified:
            return format_html('<span style="color: #ffc107;">●</span> Partiel')
        return format_html('<span style="color: #dc3545;">○</span> Non vérifié')

    verification_badge.short_description = _("Vérification")

    def security_badge(self, obj):
        score = obj.security_score
        if score >= 70:
            color = "#28a745"
        elif score >= 40:
            color = "#ffc107"
        else:
            color = "#dc3545"
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>%', color, score
        )

    security_badge.short_description = _("Sécurité")

    def security_score_display(self, obj):
        summary = obj.get_security_summary()
        html = f"""
        <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
            <h4 style="margin: 0 0 10px;">Score: {summary['score']}% ({summary['level']})</h4>
            <ul style="margin: 0; padding-left: 20px;">
                <li>Email: {'✅' if summary['has_email'] else '❌'} 
                    (vérifié: {'✅' if summary['email_verified'] else '❌'})</li>
                <li>Téléphone: {'✅' if summary['has_phone'] else '❌'} 
                    (vérifié: {'✅' if summary['phone_verified'] else '❌'})</li>
                <li>Contact secours: {'✅' if summary['has_backup_phone'] else '❌'}</li>
                <li>Questions sécurité: {summary['security_questions_count']}/3</li>
            </ul>
        </div>
        """
        if summary["suggestions"]:
            html += "<h5>Suggestions:</h5><ul>"
            for s in summary["suggestions"]:
                html += f"<li>⚠️ {s}</li>"
            html += "</ul>"
        return format_html(html)

    security_score_display.short_description = _("Détails sécurité")

    def verification_status_display(self, obj):
        html = f"""
        <div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">
            <p><strong>Email:</strong> {obj.email or 'Non configuré'} 
                {'✅ Vérifié' if obj.email_verified else '❌ Non vérifié'}</p>
            <p><strong>Téléphone:</strong> {obj.phone or 'Non configuré'} 
                {'✅ Vérifié' if obj.phone_verified else '❌ Non vérifié'}</p>
        </div>
        """
        return format_html(html)

    verification_status_display.short_description = _("Statut vérification")


@admin.register(SecurityQuestion)
class SecurityQuestionAdmin(admin.ModelAdmin):
    list_display = ["user", "question_preview", "order", "created_at"]
    list_filter = ["order", "created_at"]
    search_fields = ["user__email", "user__phone", "question"]
    raw_id_fields = ["user"]

    def question_preview(self, obj):
        return obj.question[:50] + "..." if len(obj.question) > 50 else obj.question

    question_preview.short_description = _("Question")


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ["user", "type", "purpose", "status_badge", "attempts", "created_at"]
    list_filter = ["type", "purpose", "is_used", "created_at"]
    search_fields = ["user__email", "user__phone"]
    raw_id_fields = ["user"]
    readonly_fields = ["code", "created_at"]

    def status_badge(self, obj):
        if obj.is_used:
            return format_html('<span style="color: gray;">Utilisé</span>')
        elif obj.is_expired:
            return format_html('<span style="color: #dc3545;">Expiré</span>')
        return format_html('<span style="color: #28a745;">Actif</span>')

    status_badge.short_description = _("Statut")


@admin.register(PhoneHistory)
class PhoneHistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "phone", "verified", "reason", "removed_at"]
    list_filter = ["verified", "reason", "removed_at"]
    search_fields = ["user__email", "phone"]
    raw_id_fields = ["user"]


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    list_display = [
        "identifier",
        "status_badge",
        "failure_reason",
        "ip_address",
        "created_at",
    ]
    list_filter = ["success", "failure_reason", "created_at"]
    search_fields = ["identifier", "ip_address"]
    raw_id_fields = ["user"]
    readonly_fields = ["created_at"]

    def status_badge(self, obj):
        if obj.success:
            return format_html('<span style="color: #28a745;">✓ Réussi</span>')
        return format_html('<span style="color: #dc3545;">✗ Échec</span>')

    status_badge.short_description = _("Statut")
