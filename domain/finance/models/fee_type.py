from django.db import models

from domain.finance.constants import FeeCategory, PaymentFrequency
from domain.shared.models.base import AuditModel


class FeeType(AuditModel):
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=FeeCategory.choices)
    description = models.TextField(null=True, blank=True)
    default_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_frequency = models.CharField(max_length=10, choices=PaymentFrequency.choices)

    class Meta:
        db_table = "fee_type"
        verbose_name = "Fee Type"
        verbose_name_plural = "Fee Types"
        ordering = ["category", "name"]

    def __str__(self):
        return f"{self.get_category_display()} - {self.name}"
