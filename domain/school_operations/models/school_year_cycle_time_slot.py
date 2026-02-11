"""SchoolYearCycleTimeSlot model."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.school_operations.constants import TimeSlotStatus
from domain.school_operations.models.school_year_cycle import SchoolYearCycle
from domain.shared.models.base import AuditModel


class SchoolYearCycleTimeSlot(AuditModel):
    """
    Time slot (créneau horaire) for a specific SchoolYearCycle.
    
    Used for scheduling/timetable: defines available periods during the day
    for a specific cycle (e.g., "8h-9h", "9h-10h").
    
    Business Rules:
        - Unique per (school_year_cycle, name) for non-deleted records
        - start_time < end_time
        - order helps define sequence during the day
        - Cannot overlap with other time slots in same cycle (validation optional)
    """

    school_year_cycle = models.ForeignKey(
        SchoolYearCycle,
        on_delete=models.PROTECT,
        related_name="time_slots",
        help_text="School year cycle for this time slot",
    )
    name = models.CharField(
        max_length=100,
        help_text="Display name (e.g., 'Période 1', '8h-9h')",
    )
    start_time = models.TimeField(
        help_text="Start time of the slot",
    )
    end_time = models.TimeField(
        help_text="End time of the slot",
    )
    order = models.PositiveSmallIntegerField(
        default=1,
        help_text="Order/sequence within the day",
    )
    status = models.CharField(
        max_length=20,
        choices=TimeSlotStatus.choices,
        default=TimeSlotStatus.ACTIVE,
        help_text="Status of the time slot",
    )

    class Meta:
        db_table = "school_year_cycle_time_slot"
        verbose_name = "School Year Cycle Time Slot"
        verbose_name_plural = "School Year Cycle Time Slots"
        ordering = ["school_year_cycle", "order", "start_time"]
        indexes = [
            models.Index(fields=["school_year_cycle", "order"], name="syc_timeslot_order_idx"),
            models.Index(fields=["start_time", "end_time"], name="syc_timeslot_time_idx"),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=["school_year_cycle", "name"],
                condition=models.Q(is_deleted=False),
                name="unique_school_year_cycle_time_slot",
            ),
            models.CheckConstraint(
                condition=models.Q(start_time__lt=models.F("end_time")),
                name="school_year_cycle_time_slot_times_valid",
            ),
        ]

    def __str__(self) -> str:
        return f"{self.school_year_cycle} - {self.name} ({self.start_time}-{self.end_time})"

    def clean(self):
        super().clean()

        # Time coherence
        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError({"end_time": "End time must be after start time."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
