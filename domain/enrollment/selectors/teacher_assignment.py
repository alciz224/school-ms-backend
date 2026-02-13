from django.db.models import QuerySet

from domain.enrollment.constants import TeacherAssignmentStatus
from domain.enrollment.models import TeacherAssignment


class TeacherAssignmentSelector:
    @staticmethod
    def list(
        *,
        classroom_id: int | None = None,
        school_year_teacher_id: int | None = None,
        status: str | None = None,
    ) -> QuerySet[TeacherAssignment]:
        """List teacher assignments with optional filters."""
        qs = TeacherAssignment.objects.select_related(
            "school_year_teacher__teacher",
            "classroom", 
            "school_year_level_subject__subject",
            "school_year_level_subject__school_year_level",
        )
        
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        if school_year_teacher_id:
            qs = qs.filter(school_year_teacher_id=school_year_teacher_id)
        if status:
            qs = qs.filter(assignment_status=status)
            
        return qs.order_by("classroom__name", "school_year_level_subject__subject__name")

    @staticmethod
    def get(*, assignment_id: int) -> TeacherAssignment:
        """Get a single teacher assignment by ID."""
        return TeacherAssignment.objects.select_related(
            "school_year_teacher__teacher",
            "classroom",
            "school_year_level_subject__subject",
            "school_year_level_subject__school_year_level",
        ).get(id=assignment_id)

    @staticmethod
    def get_active_assignments(
        *, teacher_user_id: int | None = None, classroom_id: int | None = None
    ) -> QuerySet[TeacherAssignment]:
        """Get active teacher assignments."""
        qs = TeacherAssignment.objects.filter(
            assignment_status=TeacherAssignmentStatus.ACTIVE,
            is_deleted=False,
        ).select_related(
            "school_year_teacher__teacher",
            "classroom",
            "school_year_level_subject__subject",
            "school_year_level_subject__school_year_level",
        )
        
        if teacher_user_id:
            qs = qs.filter(school_year_teacher__teacher_id=teacher_user_id)
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
            
        return qs

    @staticmethod
    def get_teacher_classes(*, teacher_user_id: int) -> QuerySet[TeacherAssignment]:
        """
        Get all active classes for a teacher (for teacher portal).
        
        Returns active assignments grouped by classroom.
        """
        return TeacherAssignmentSelector.get_active_assignments(
            teacher_user_id=teacher_user_id
        ).order_by("classroom__name", "school_year_level_subject__subject__name")

    @staticmethod
    def get_teacher_classroom_ids(*, teacher_user_id: int):
        """
        Get IDs of all classrooms where a teacher has active assignments.
        
        Used for filtering classroom access in teacher portal.
        """
        from typing import List
        return list(
            TeacherAssignment.objects.filter(
                school_year_teacher__teacher_id=teacher_user_id,
                assignment_status=TeacherAssignmentStatus.ACTIVE,
                is_deleted=False,
            ).values_list("classroom_id", flat=True).distinct()
        )

    @staticmethod
    def get_classroom_teachers(*, classroom_id: int) -> QuerySet[TeacherAssignment]:
        """
        Get all active teachers for a classroom (for admin portal).
        
        Returns active assignments for a specific classroom.
        """
        return TeacherAssignmentSelector.get_active_assignments(
            classroom_id=classroom_id
        ).order_by("school_year_level_subject__subject__name")

    @staticmethod
    def get_active_assignment_for_classroom_subject(
        *, classroom_id: int, school_year_level_subject_id: int
    ) -> TeacherAssignment | None:
        """
        Get the active teacher assignment for a specific classroom+subject.
        
        Used to check existing assignments before creating new ones.
        """
        return TeacherAssignment.objects.filter(
            classroom_id=classroom_id,
            school_year_level_subject_id=school_year_level_subject_id,
            assignment_status=TeacherAssignmentStatus.ACTIVE,
            is_deleted=False,
        ).select_related(
            "school_year_teacher__teacher",
        ).first()

    @staticmethod
    def get_assignment_history(
        *, classroom_id: int | None = None, school_year_level_subject_id: int | None = None
    ) -> QuerySet[TeacherAssignment]:
        """
        Get assignment history for a classroom+subject (including replacements).
        
        Useful for audit and to understand replacement chains.
        """
        qs = TeacherAssignment.objects.select_related(
            "school_year_teacher__teacher",
            "replaced_by__school_year_teacher__teacher",
        )
        
        if classroom_id:
            qs = qs.filter(classroom_id=classroom_id)
        if school_year_level_subject_id:
            qs = qs.filter(school_year_level_subject_id=school_year_level_subject_id)
            
        return qs.order_by("start_date")