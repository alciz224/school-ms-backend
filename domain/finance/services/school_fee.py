from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from domain.finance.models import SchoolFee
from domain.finance.selectors.school_fee import SchoolFeeSelector


class SchoolFeeService:
    @staticmethod
    @transaction.atomic
    def create(
        *,
        school_year_id: int,
        school_year_level_id: int,
        fee_type_id: int,
        amount: float,
        due_date,
        school_year_cycle_id: Optional[int] = None,
        is_mandatory: bool = True,
        created_by=None,
    ) -> SchoolFee:
        if SchoolFeeSelector.exists(
            school_year_id=school_year_id,
            school_year_level_id=school_year_level_id,
            fee_type_id=fee_type_id,
            school_year_cycle_id=school_year_cycle_id,
        ):
            raise ValidationError(
                _("This fee is already assigned to this level for the selected cycle.")
            )

        school_fee = SchoolFee(
            school_year_id=school_year_id,
            school_year_level_id=school_year_level_id,
            fee_type_id=fee_type_id,
            amount=amount,
            due_date=due_date,
            school_year_cycle_id=school_year_cycle_id,
            is_mandatory=is_mandatory,
            created_by=created_by,
            updated_by=created_by,
        )
        school_fee.save()
        return school_fee

    @staticmethod
    @transaction.atomic
    def update(
        *,
        school_fee: SchoolFee,
        amount: Optional[float] = None,
        due_date=None,
        is_mandatory: Optional[bool] = None,
        updated_by=None,
    ) -> SchoolFee:
        if amount is not None:
            school_fee.amount = amount
        if due_date is not None:
            school_fee.due_date = due_date
        if is_mandatory is not None:
            school_fee.is_mandatory = is_mandatory
        school_fee.updated_by = updated_by
        school_fee.save()
        return school_fee

    @staticmethod
    @transaction.atomic
    def delete(*, school_fee: SchoolFee, deleted_by=None) -> None:
        if school_fee.payments.exists():
            raise ValidationError(
                _("Cannot delete a fee with existing payments.")
            )
        school_fee.soft_delete(user=deleted_by)
