"""Schedule service for business logic."""

from datetime import date
from typing import Optional

from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

from domain.scheduling.constants import ScheduleStatus, SCHEDULE_STATUS_TRANSITIONS
from domain.scheduling.models import Schedule


class ScheduleConflictError(ValidationError):
    """Raised when a scheduling conflict is detected."""
    pass


class ScheduleService:
    """Service for Schedule business logic."""

    @staticmethod
    @transaction.atomic
    def create(*, data: dict) -> Schedule:
        """
        Create a new schedule with conflict validation.
        
        Args:
            data: Dictionary with schedule fields
            
        Returns:
            Created Schedule instance
            
        Raises:
            ValidationError: If validation fails
            ScheduleConflictError: If scheduling conflicts detected
        """
        # Extract data
        classroom_id = data.get('classroom_id')
        teacher_assignment_id = data.get('teacher_assignment_id')
        day_of_week = data.get('day_of_week')
        time_slot_id = data.get('time_slot_id')
        effective_from = data.get('effective_from')
        effective_to = data.get('effective_to')
        status = data.get('status', ScheduleStatus.DRAFT)
        
        # Create schedule instance for validation
        schedule = Schedule(**data)
        
        # Run model validation
        schedule.full_clean()
        
        # Check for conflicts (only for ACTIVE schedules)
        if status == ScheduleStatus.ACTIVE:
            conflicts = ScheduleService.detect_conflicts(
                classroom_id=classroom_id,
                teacher_assignment_id=teacher_assignment_id,
                day_of_week=day_of_week,
                time_slot_id=time_slot_id,
                effective_from=effective_from,
                effective_to=effective_to,
            )
            
            if conflicts['has_conflicts']:
                error_msg = "Scheduling conflicts detected:\n"
                if conflicts['classroom_conflicts']:
                    error_msg += f"- Classroom conflicts: {len(conflicts['classroom_conflicts'])}\n"
                if conflicts['teacher_conflicts']:
                    error_msg += f"- Teacher conflicts: {len(conflicts['teacher_conflicts'])}\n"
                raise ScheduleConflictError(error_msg)
        
        # Save schedule
        schedule.save()
        return schedule

    @staticmethod
    @transaction.atomic
    def update(*, schedule_id: int, data: dict) -> Schedule:
        """
        Update an existing schedule.
        
        Args:
            schedule_id: ID of schedule to update
            data: Dictionary with fields to update
            
        Returns:
            Updated Schedule instance
            
        Raises:
            Schedule.DoesNotExist: If schedule not found
            ValidationError: If update not allowed or validation fails
        """
        schedule = Schedule.objects.get(id=schedule_id, is_deleted=False)
        
        # Check if can modify
        if not schedule.can_modify():
            raise ValidationError(_("Cannot modify archived schedules."))
        
        # Check if timing changed and status is ACTIVE
        timing_changed = any(
            data.get(field) and data.get(field) != getattr(schedule, field)
            for field in ['day_of_week', 'time_slot_id', 'effective_from', 'effective_to']
        )
        
        if timing_changed and (data.get('status', schedule.status) == ScheduleStatus.ACTIVE):
            # Re-check conflicts with new timing
            conflicts = ScheduleService.detect_conflicts(
                classroom_id=data.get('classroom_id', schedule.classroom_id),
                teacher_assignment_id=data.get('teacher_assignment_id', schedule.teacher_assignment_id),
                day_of_week=data.get('day_of_week', schedule.day_of_week),
                time_slot_id=data.get('time_slot_id', schedule.time_slot_id),
                effective_from=data.get('effective_from', schedule.effective_from),
                effective_to=data.get('effective_to', schedule.effective_to),
                exclude_schedule_id=schedule_id,
            )
            
            if conflicts['has_conflicts']:
                raise ScheduleConflictError(_("Update would create scheduling conflicts."))
        
        # Update fields
        for field, value in data.items():
            if hasattr(schedule, field):
                setattr(schedule, field, value)
        
        # Validate and save
        schedule.full_clean()
        schedule.save()
        return schedule

    @staticmethod
    @transaction.atomic
    def delete(*, schedule_id: int) -> None:
        """
        Soft delete a schedule.
        
        Args:
            schedule_id: ID of schedule to delete
            
        Raises:
            Schedule.DoesNotExist: If schedule not found
            ValidationError: If delete not allowed
        """
        schedule = Schedule.objects.get(id=schedule_id, is_deleted=False)
        
        if not schedule.can_delete():
            raise ValidationError(_("Cannot delete archived schedules."))
        
        schedule.is_deleted = True
        schedule.save()

    @staticmethod
    @transaction.atomic
    def change_status(*, schedule_id: int, new_status: str) -> Schedule:
        """
        Change schedule status with validation.
        
        Args:
            schedule_id: ID of schedule
            new_status: New status value
            
        Returns:
            Updated Schedule instance
            
        Raises:
            Schedule.DoesNotExist: If schedule not found
            ValidationError: If status transition not allowed
        """
        schedule = Schedule.objects.get(id=schedule_id, is_deleted=False)
        
        # Validate status transition
        current_status = schedule.status
        allowed_transitions = SCHEDULE_STATUS_TRANSITIONS.get(current_status, [])
        
        if new_status not in allowed_transitions:
            raise ValidationError(
                _(f"Cannot transition from {current_status} to {new_status}. "
                  f"Allowed transitions: {', '.join(allowed_transitions)}")
            )
        
        # If changing to ACTIVE, check conflicts
        if new_status == ScheduleStatus.ACTIVE:
            conflicts = ScheduleService.detect_conflicts(
                classroom_id=schedule.classroom_id,
                teacher_assignment_id=schedule.teacher_assignment_id,
                day_of_week=schedule.day_of_week,
                time_slot_id=schedule.time_slot_id,
                effective_from=schedule.effective_from,
                effective_to=schedule.effective_to,
                exclude_schedule_id=schedule_id,
            )
            
            if conflicts['has_conflicts']:
                raise ScheduleConflictError(_("Cannot activate schedule due to conflicts."))
        
        schedule.status = new_status
        schedule.save()
        return schedule

    @staticmethod
    def detect_conflicts(
        *,
        classroom_id: int,
        teacher_assignment_id: int,
        day_of_week: str,
        time_slot_id: int,
        effective_from: date,
        effective_to: Optional[date] = None,
        exclude_schedule_id: Optional[int] = None,
    ) -> dict:
        """
        Detect scheduling conflicts without creating a schedule.
        
        Args:
            classroom_id: Classroom ID
            teacher_assignment_id: Teacher assignment ID
            day_of_week: Day of week
            time_slot_id: Time slot ID
            effective_from: Start date
            effective_to: End date (optional)
            exclude_schedule_id: Schedule ID to exclude (for updates)
            
        Returns:
            Dictionary with conflict information:
            {
                "has_conflicts": bool,
                "classroom_conflicts": [list of conflicting schedules],
                "teacher_conflicts": [list of conflicting schedules]
            }
        """
        from domain.enrollment.models import TeacherAssignment
        
        # Get teacher from assignment
        teacher_assignment = TeacherAssignment.objects.get(id=teacher_assignment_id)
        teacher_id = teacher_assignment.school_year_teacher.teacher_id
        
        # Build date overlap query
        date_overlap_q = Q(
            effective_from__lte=effective_to if effective_to else effective_from
        ) & (
            Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from)
        )
        
        # Base query for conflicts
        base_q = (
            Q(day_of_week=day_of_week) &
            Q(time_slot_id=time_slot_id) &
            Q(status=ScheduleStatus.ACTIVE) &
            Q(is_deleted=False) &
            date_overlap_q
        )
        
        if exclude_schedule_id:
            base_q &= ~Q(id=exclude_schedule_id)
        
        # Check classroom conflicts
        classroom_conflicts = list(
            Schedule.objects.filter(base_q & Q(classroom_id=classroom_id))
            .select_related('classroom', 'teacher_assignment__school_year_teacher__teacher')
        )
        
        # Check teacher conflicts (same teacher, different classroom)
        teacher_conflicts = list(
            Schedule.objects.filter(
                base_q & 
                Q(teacher_assignment__school_year_teacher__teacher_id=teacher_id) &
                ~Q(classroom_id=classroom_id)
            ).select_related('classroom', 'teacher_assignment__school_year_teacher__teacher')
        )
        
        return {
            "has_conflicts": bool(classroom_conflicts or teacher_conflicts),
            "classroom_conflicts": classroom_conflicts,
            "teacher_conflicts": teacher_conflicts,
        }

    @staticmethod
    @transaction.atomic
    def bulk_create(*, schedules_data: list) -> dict:
        """
        Create multiple schedules with validation.
        
        Args:
            schedules_data: List of dictionaries with schedule data
            
        Returns:
            Dictionary with:
            {
                "created": [list of created schedules],
                "failed": [list of {data, errors}]
            }
        """
        created = []
        failed = []
        
        for data in schedules_data:
            try:
                schedule = ScheduleService.create(data=data)
                created.append(schedule)
            except (ValidationError, ScheduleConflictError) as e:
                failed.append({
                    "data": data,
                    "errors": str(e),
                })
        
        return {
            "created": created,
            "failed": failed,
        }
