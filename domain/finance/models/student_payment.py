from django.db import models

from domain.enrollment.models import StudentEnrollment
from domain.finance.constants import PaymentMethod
from domain.finance.models.school_fee import SchoolFee
from domain.shared.models.base import AuditModel


class StudentPayment(AuditModel):
    student_enrollment = models.ForeignKey(
        StudentEnrollment, on_delete=models.PROTECT, related_name="payments"
    )
    school_fee = models.ForeignKey(
        SchoolFee, on_delete=models.PROTECT, related_name="payments"
    )
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    reference_number = models.CharField(max_length=100, null=True, blank=True)
    collected_by = models.CharField(max_length=200, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    class Meta:
        db_table = "student_payment"
        verbose_name = "Student Payment"
        verbose_name_plural = "Student Payments"
        ordering = ["-payment_date", "-created_at"]
        indexes = [
            models.Index(fields=["student_enrollment"], name="payment_enrollment_idx"),
            models.Index(fields=["school_fee"], name="payment_fee_idx"),
            models.Index(fields=["payment_date"], name="payment_date_idx"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(amount_paid__gt=0),
                name="payment_amount_positive",
            ),
        ]

    def __str__(self):
        return f"{self.student_enrollment} - {self.school_fee.fee_type.name} - {self.amount_paid}"
