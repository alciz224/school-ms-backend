"""Schedule model for timetable management."""

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from domain.enrollment.constants import TeacherAssignmentStatus
from domain.enrollment.models import Classroom, TeacherAssignment
from domain.scheduling.constants import DayOfWeek, ScheduleStatus
from domain.school_operations.models import SchoolYear, SchoolYearCycle, SchoolYearCycleTimeSlot
from domain.shared.models.base import AuditModel


class Schedule(AuditModel):
    """
    Represents a single scheduled class session (one time slot, one day).
    
    The Schedule is an organizational projection: it consumes existing TeacherAssignments
    and organizes them into a weekly timetable.
    
    Business Rules:
        - teacher_assignment must have status ACTIVE
        - No time conflicts for same classroom at same (day_of_week, time_slot, effective period)
        - No time conflicts for same teacher at same (day_of_week, time_slot, effective period)
        - time_slot must belong to school_year_cycle
        - classroom must match teacher_assignment.classroom
        - effective_from < effective_to (if effective_to is set)
        - effective_from must be within school_year period
        - status workflow: DRAFT → ACTIVE → SUSPENDED → ARCHIVED
        - Cannot modify ARCHIVED schedules
        
    Workflow:
        - Create: status=DRAFT, prepare timetable
        - Activate: status=ACTIVE, make official
        - Suspend: status=SUSPENDED, temporarily disable
        - Archive: status=ARCHIVED, preserve history
    """

    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name="schedules",
        help_text="School year for this schedule",
    )
    school_year_cycle = models.ForeignKey(
        SchoolYearCycle,
        on_delete=models.PROTECT,
        related_name="schedules",
        help_text="Cycle within the school year",
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="schedules",
        help_text="Classroom where the session takes place",
    )
    teacher_assignment = models.ForeignKey(
        TeacherAssignment,
        on_delete=models.PROTECT,
        related_name="schedules",
        help_text="Teacher assignment (must be ACTIVE)",
    )
    day_of_week = models.CharField(
        max_length=10,
        choices=DayOfWeek.choices,
        help_text="Day of the week",
    )
    time_slot = models.ForeignKey(
        SchoolYearCycleTimeSlot,
        on_delete=models.PROTECT,
        related_name="schedules",
        help_text="Time slot for this session",
    )
    effective_from = models.DateField(
        help_text="Date when this schedule becomes effective",
    )
    effective_to = models.DateField(
        null=True,
        blank=True,
        help_text="Date when this schedule ends (nullable for ongoing)",
    )
    status = models.CharField(
        max_length=20,
        choices=ScheduleStatus.choices,
        default=ScheduleStatus.DRAFT,
        help_text="Status of the schedule",
    )

    class Meta:
        db_table = "schedule"
        verbose_name = "Schedule"
        verbose_name_plural = "Schedules"
        ordering = ["school_year_cycle", "classroom", "day_of_week", "time_slot__order"]
        indexes = [
            # For conflict detection
            models.Index(
                fields=["classroom", "day_of_week", "time_slot", "status"],
                name="schedule_classroom_slot_idx",
            ),
            models.Index(
                fields=["teacher_assignment", "day_of_week", "time_slot"],
                name="schedule_teacher_slot_idx",
            ),
            # For date-based queries
            models.Index(
                fields=["effective_from", "effective_to"],
                name="schedule_effective_dates_idx",
            ),
            # For timetable views
            models.Index(
                fields=["school_year_cycle", "classroom", "day_of_week"],
                name="schedule_timetable_idx",
            ),
        ]
        constraints = [
            # Date coherence
            models.CheckConstraint(
                condition=models.Q(effective_to__isnull=True) | models.Q(effective_from__lt=models.F("effective_to")),
                name="schedule_dates_coherent",
            ),
        ]

    def __str__(self) -> str:
        subject = self.teacher_assignment.subject.name
        classroom = self.classroom.name
        day = self.get_day_of_week_display()
        time = f"{self.time_slot.start_time}-{self.time_slot.end_time}"
        return f"{classroom} - {subject} ({day} {time}) [{self.status}]"

    def clean(self):
        """Validate model fields and business rules."""
        super().clean()

        # 1. Validate teacher_assignment is ACTIVE
        if self.teacher_assignment_id:
            if self.teacher_assignment.assignment_status != TeacherAssignmentStatus.ACTIVE:
                raise ValidationError({
                    "teacher_assignment": _("Only ACTIVE teacher assignments can be scheduled.")
                })

        # 2. Validate time_slot belongs to school_year_cycle
        if self.time_slot_id and self.school_year_cycle_id:
            if self.time_slot.school_year_cycle_id != self.school_year_cycle_id:
                raise ValidationError({
                    "time_slot": _("Time slot must belong to the school year cycle.")
                })

        # 3. Validate classroom matches teacher_assignment
        if self.classroom_id and self.teacher_assignment_id:
            if self.classroom_id != self.teacher_assignment.classroom_id:
                raise ValidationError({
                    "classroom": _("Classroom must match teacher assignment classroom.")
                })

        # 4. Validate school_year_cycle matches classroom
        if self.school_year_cycle_id and self.classroom_id:
            if self.school_year_cycle_id != self.classroom.school_year_level.school_year_cycle_id:
                raise ValidationError({
                    "school_year_cycle": _("School year cycle must match classroom's cycle.")
                })

        # 5. Validate effective dates
        if self.effective_from and self.effective_to:
            if self.effective_from >= self.effective_to:
                raise ValidationError({
                    "effective_to": _("effective_to must be after effective_from.")
                })

        # 6. Validate effective_from within school year
        if self.school_year_id and self.effective_from:
            school_year = self.school_year
            if self.effective_from < school_year.start_date or self.effective_from > school_year.end_date:
                raise ValidationError({
                    "effective_from": _("effective_from must be within school year period.")
                })

    def save(self, *args, **kwargs):
        """Override save to run validation."""
        self.full_clean()
        super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        """Check if schedule is currently active."""
        return self.status == ScheduleStatus.ACTIVE and not self.is_deleted

    @property
    def is_archived(self) -> bool:
        """Check if schedule is archived."""
        return self.status == ScheduleStatus.ARCHIVED

    @property
    def teacher(self):
        """Shortcut to access the teacher."""
        return self.teacher_assignment.teacher

    @property
    def subject(self):
        """Shortcut to access the subject."""
        return self.teacher_assignment.subject

    def can_modify(self) -> bool:
        """Check if schedule can be modified."""
        return self.status != ScheduleStatus.ARCHIVED and not self.is_deleted

    def can_delete(self) -> bool:
        """Check if schedule can be deleted."""
        # Schedules can be soft-deleted unless archived
        return self.status != ScheduleStatus.ARCHIVED and not self.is_deleted
