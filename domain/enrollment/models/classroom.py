"""Classroom model (Enrollment domain)."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.school_operations.models import SchoolYearLevel
from domain.shared.models.base import AuditModel


class Classroom(AuditModel):
    """
    Classroom represents a physical/pedagogical class for a specific SchoolYearLevel.

    Business rules:
    - Unique per (school_year_level, name) for non-deleted records.
    - capacity must be >= 0 if provided.
    """

    school_year_level = models.ForeignKey(
        SchoolYearLevel,
        on_delete=models.PROTECT,
        related_name="classrooms",
    )
    name = models.CharField(max_length=120)
    capacity = models.PositiveIntegerField(null=True, blank=True)
    room_number = models.CharField(max_length=50, null=True, blank=True)

    class Meta:
        db_table = "classroom"
        verbose_name = "Classroom"
        verbose_name_plural = "Classrooms"
        ordering = ["school_year_level", "name"]
        indexes = [
            models.Index(fields=["school_year_level", "name"], name="classroom_syl_name_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year_level", "name"],
                condition=models.Q(is_deleted=False),
                name="unique_classroom_per_school_year_level",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.school_year_level} - {self.name}"

    def clean(self):
        super().clean()
        if self.capacity is not None and self.capacity < 0:
            raise ValidationError({"capacity": "Capacity must be >= 0."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
