"""Constants for scheduling domain."""

from django.db import models


class DayOfWeek(models.TextChoices):
    """Days of the week for scheduling."""
    MONDAY = "MONDAY", "Monday"
    TUESDAY = "TUESDAY", "Tuesday"
    WEDNESDAY = "WEDNESDAY", "Wednesday"
    THURSDAY = "THURSDAY", "Thursday"
    FRIDAY = "FRIDAY", "Friday"
    SATURDAY = "SATURDAY", "Saturday"
    SUNDAY = "SUNDAY", "Sunday"


class ScheduleStatus(models.TextChoices):
    """Status values for schedules."""
    DRAFT = "DRAFT", "Draft"              # Being prepared, not visible to students/teachers
    ACTIVE = "ACTIVE", "Active"           # Currently in use and official
    SUSPENDED = "SUSPENDED", "Suspended"  # Temporarily disabled (e.g., strike, reorganization)
    ARCHIVED = "ARCHIVED", "Archived"     # Historical record, read-only


# Valid status transitions
SCHEDULE_STATUS_TRANSITIONS = {
    ScheduleStatus.DRAFT: [ScheduleStatus.ACTIVE],
    ScheduleStatus.ACTIVE: [ScheduleStatus.SUSPENDED, ScheduleStatus.ARCHIVED],
    ScheduleStatus.SUSPENDED: [ScheduleStatus.ACTIVE, ScheduleStatus.ARCHIVED],
    ScheduleStatus.ARCHIVED: [],  # Cannot transition from archived
}
