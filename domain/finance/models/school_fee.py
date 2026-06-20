from django.core.exceptions import ValidationError
from django.db import models

from domain.finance.models.fee_type import FeeType
from domain.school_operations.models import SchoolYear, SchoolYearLevel, SchoolYearCycle
from domain.shared.models.base import AuditModel


class SchoolFee(AuditModel):
    school_year = models.ForeignKey(
        SchoolYear, on_delete=models.PROTECT, related_name="fees"
    )
    school_year_level = models.ForeignKey(
        SchoolYearLevel, on_delete=models.PROTECT, related_name="fees"
    )
    fee_type = models.ForeignKey(
        FeeType, on_delete=models.PROTECT, related_name="school_fees"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    school_year_cycle = models.ForeignKey(
        SchoolYearCycle,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="fees",
    )
    is_mandatory = models.BooleanField(default=True)

    class Meta:
        db_table = "school_fee"
        verbose_name = "School Fee"
        verbose_name_plural = "School Fees"
        ordering = ["school_year", "school_year_level", "fee_type"]
        indexes = [
            models.Index(fields=["school_year", "school_year_level"], name="school_fee_year_level_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year", "school_year_level", "fee_type", "school_year_cycle"],
                condition=models.Q(is_deleted=False),
                name="unique_school_fee_assignment",
            ),
            models.CheckConstraint(
                condition=models.Q(amount__gte=0),
                name="school_fee_amount_non_negative",
            ),
        ]

    def __str__(self):
        return f"{self.school_year} - {self.school_year_level} - {self.fee_type}"

    def clean(self):
        super().clean()
        if self.amount is not None and self.amount < 0:
            raise ValidationError({"amount": "Amount cannot be negative."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
