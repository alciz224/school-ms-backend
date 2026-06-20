from datetime import date
from decimal import Decimal
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from domain.finance.models import SchoolFee, StudentPayment


class StudentPaymentService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        student_enrollment_id: int,
        school_fee_id: int,
        amount_paid: Decimal,
        payment_date: date,
        payment_method: str,
        reference_number: Optional[str] = None,
        collected_by: Optional[str] = None,
        notes: Optional[str] = None,
        created_by=None,
    ) -> StudentPayment:
        try:
            school_fee = SchoolFee.objects.get(id=school_fee_id, is_deleted=False)
        except SchoolFee.DoesNotExist:
            raise ValidationError(_("School fee not found."))

        total_paid = sum(
            (p.amount_paid for p in school_fee.payments.all()),
            Decimal("0.00"),
        )
        balance = school_fee.amount - total_paid
        if amount_paid > balance:
            raise ValidationError(
                _("Payment amount (%(amount)s) exceeds remaining balance (%(balance)s).")
                % {"amount": amount_paid, "balance": balance}
            )

        payment = StudentPayment(
            student_enrollment_id=student_enrollment_id,
            school_fee=school_fee,
            amount_paid=amount_paid,
            payment_date=payment_date,
            payment_method=payment_method,
            reference_number=reference_number,
            collected_by=collected_by,
            notes=notes,
            created_by=created_by,
            updated_by=created_by,
        )
        payment.save()
        return payment
