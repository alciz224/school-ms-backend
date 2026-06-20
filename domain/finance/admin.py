from django.contrib import admin

from domain.finance.models import FeeType, SchoolFee, StudentPayment


@admin.register(FeeType)
class FeeTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "default_amount", "payment_frequency", "is_active"]
    list_filter = ["category", "payment_frequency", "is_active"]
    search_fields = ["name"]


@admin.register(SchoolFee)
class SchoolFeeAdmin(admin.ModelAdmin):
    list_display = ["school_year", "school_year_level", "fee_type", "amount", "due_date", "is_mandatory"]
    list_filter = ["is_mandatory", "school_year"]
    search_fields = ["fee_type__name"]


@admin.register(StudentPayment)
class StudentPaymentAdmin(admin.ModelAdmin):
    list_display = ["student_enrollment", "school_fee", "amount_paid", "payment_date", "payment_method"]
    list_filter = ["payment_method", "payment_date"]
    search_fields = ["student_enrollment__student__user__email"]
