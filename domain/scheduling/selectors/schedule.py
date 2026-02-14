"""Schedule selectors for database queries."""

from datetime import date
from typing import Optional

from django.db.models import Q, QuerySet

from domain.scheduling.constants import ScheduleStatus
from domain.scheduling.models import Schedule


class ScheduleSelector:
    """Selector for Schedule queries."""

    @staticmethod
    def get_all(
        *,
        school_year_id: Optional[int] = None,
        school_year_cycle_id: Optional[int] = None,
        status: Optional[str] = None,
    ) -> QuerySet[Schedule]:
        """
        Get all schedules with optional filters.
        
        Args:
            school_year_id: Filter by school year
            school_year_cycle_id: Filter by school year cycle
            status: Filter by status
            
        Returns:
            QuerySet of schedules
        """
        qs = Schedule.objects.filter(is_deleted=False).select_related(
            'school_year',
            'school_year_cycle',
            'classroom',
            'teacher_assignment__school_year_teacher__teacher',
            'teacher_assignment__school_year_level_subject__subject',
            'time_slot',
        )
        
        if school_year_id:
            qs = qs.filter(school_year_id=school_year_id)
        if school_year_cycle_id:
            qs = qs.filter(school_year_cycle_id=school_year_cycle_id)
        if status:
            qs = qs.filter(status=status)
        
        return qs

    @staticmethod
    def get_by_id(*, schedule_id: int) -> Schedule:
        """
        Get a single schedule by ID.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            Schedule instance
            
        Raises:
            Schedule.DoesNotExist: If not found
        """
        return Schedule.objects.select_related(
            'school_year',
            'school_year_cycle',
            'classroom',
            'teacher_assignment__school_year_teacher__teacher',
            'teacher_assignment__school_year_level_subject__subject',
            'time_slot',
        ).get(id=schedule_id, is_deleted=False)

    @staticmethod
    def get_by_classroom(
        *,
        classroom_id: int,
        day_of_week: Optional[str] = None,
        effective_date: Optional[date] = None,
        status: str = ScheduleStatus.ACTIVE,
    ) -> QuerySet[Schedule]:
        """
        Get classroom timetable.
        
        Args:
            classroom_id: Classroom ID
            day_of_week: Filter by specific day (optional)
            effective_date: Filter by effective date (optional)
            status: Filter by status (default: ACTIVE)
            
        Returns:
            QuerySet of schedules ordered by day and time
        """
        qs = Schedule.objects.filter(
            classroom_id=classroom_id,
            status=status,
            is_deleted=False,
        ).select_related(
            'teacher_assignment__school_year_teacher__teacher',
            'teacher_assignment__school_year_level_subject__subject',
            'time_slot',
        ).order_by('day_of_week', 'time_slot__order')
        
        if day_of_week:
            qs = qs.filter(day_of_week=day_of_week)
        
        if effective_date:
            qs = qs.filter(
                effective_from__lte=effective_date
            ).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=effective_date)
            )
        
        return qs

    @staticmethod
    def get_by_teacher(
        *,
        teacher_id: int,
        day_of_week: Optional[str] = None,
        effective_date: Optional[date] = None,
        status: str = ScheduleStatus.ACTIVE,
    ) -> QuerySet[Schedule]:
        """
        Get teacher schedule.
        
        Args:
            teacher_id: Teacher user ID
            day_of_week: Filter by specific day (optional)
            effective_date: Filter by effective date (optional)
            status: Filter by status (default: ACTIVE)
            
        Returns:
            QuerySet of schedules ordered by day and time
        """
        qs = Schedule.objects.filter(
            teacher_assignment__school_year_teacher__teacher_id=teacher_id,
            status=status,
            is_deleted=False,
        ).select_related(
            'classroom',
            'teacher_assignment__school_year_level_subject__subject',
            'time_slot',
        ).order_by('day_of_week', 'time_slot__order')
        
        if day_of_week:
            qs = qs.filter(day_of_week=day_of_week)
        
        if effective_date:
            qs = qs.filter(
                effective_from__lte=effective_date
            ).filter(
                Q(effective_to__isnull=True) | Q(effective_to__gte=effective_date)
            )
        
        return qs

    @staticmethod
    def get_by_student(
        *,
        student_id: int,
        effective_date: Optional[date] = None,
        status: str = ScheduleStatus.ACTIVE,
    ) -> QuerySet[Schedule]:
        """
        Get student timetable (via enrollment).
        
        Args:
            student_id: Student user ID
            effective_date: Filter by effective date (optional)
            status: Filter by status (default: ACTIVE)
            
        Returns:
            QuerySet of schedules ordered by day and time
        """
        from domain.enrollment.models import StudentEnrollment
        
        # Get student's current classroom
        try:
            enrollment = StudentEnrollment.objects.filter(
                student_id=student_id,
                is_deleted=False,
            ).select_related('classroom').latest('created_at')
            
            classroom_id = enrollment.classroom_id
        except StudentEnrollment.DoesNotExist:
            return Schedule.objects.none()
        
        # Return classroom schedule
        return ScheduleSelector.get_by_classroom(
            classroom_id=classroom_id,
            effective_date=effective_date,
            status=status,
        )

    @staticmethod
    def get_active_schedules(
        *,
        school_year_id: int,
        effective_date: date,
    ) -> QuerySet[Schedule]:
        """
        Get all active schedules for a specific date.
        
        Args:
            school_year_id: School year ID
            effective_date: Date to check
            
        Returns:
            QuerySet of active schedules
        """
        return Schedule.objects.filter(
            school_year_id=school_year_id,
            status=ScheduleStatus.ACTIVE,
            is_deleted=False,
            effective_from__lte=effective_date,
        ).filter(
            Q(effective_to__isnull=True) | Q(effective_to__gte=effective_date)
        ).select_related(
            'classroom',
            'teacher_assignment__school_year_teacher__teacher',
            'teacher_assignment__school_year_level_subject__subject',
            'time_slot',
        )

    @staticmethod
    def get_conflicts(
        *,
        classroom_id: Optional[int] = None,
        teacher_id: Optional[int] = None,
        day_of_week: str,
        time_slot_id: int,
        effective_from: date,
        effective_to: Optional[date] = None,
    ) -> QuerySet[Schedule]:
        """
        Find scheduling conflicts.
        
        Args:
            classroom_id: Classroom to check (optional)
            teacher_id: Teacher to check (optional)
            day_of_week: Day of week
            time_slot_id: Time slot ID
            effective_from: Start date
            effective_to: End date (optional)
            
        Returns:
            QuerySet of conflicting schedules
        """
        # Date overlap condition
        date_overlap_q = Q(
            effective_from__lte=effective_to if effective_to else effective_from
        ) & (
            Q(effective_to__isnull=True) | Q(effective_to__gte=effective_from)
        )
        
        # Base query
        base_q = (
            Q(day_of_week=day_of_week) &
            Q(time_slot_id=time_slot_id) &
            Q(status=ScheduleStatus.ACTIVE) &
            Q(is_deleted=False) &
            date_overlap_q
        )
        
        # Add classroom or teacher filter
        if classroom_id:
            base_q &= Q(classroom_id=classroom_id)
        elif teacher_id:
            base_q &= Q(teacher_assignment__school_year_teacher__teacher_id=teacher_id)
        
        return Schedule.objects.filter(base_q).select_related(
            'classroom',
            'teacher_assignment__school_year_teacher__teacher',
            'teacher_assignment__school_year_level_subject__subject',
            'time_slot',
        )
