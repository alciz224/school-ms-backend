from datetime import date

from django.db import transaction
from django.db.models import Q

from domain.enrollment.constants import TeacherAssignmentStatus
from domain.enrollment.models import TeacherAssignment
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.shared.exceptions import BusinessRuleException, ValidationException


class TeacherAssignmentService:
    @staticmethod
    def create(
        *,
        school_year_teacher,
        classroom,
        school_year_level_subject,
        start_date: date,
        user=None,
    ) -> TeacherAssignment:
        """
        Create a new ACTIVE teacher assignment.
        
        Business rules:
        - school_year_teacher must be ACTIVE
        - Only one ACTIVE assignment per (classroom, subject) allowed
        """
        # Validate prerequisite: teacher must be ACTIVE
        if school_year_teacher.status != SchoolYearTeacherStatus.ACTIVE:
            raise BusinessRuleException(
                rule="teacher_not_active",
                message=f"Teacher {school_year_teacher.teacher} is not active in this school year.",
            )

        # Check for existing ACTIVE assignment for this classroom+subject
        existing = TeacherAssignment.objects.filter(
            classroom=classroom,
            school_year_level_subject=school_year_level_subject,
            assignment_status=TeacherAssignmentStatus.ACTIVE,
            is_deleted=False,
        ).first()

        if existing:
            raise BusinessRuleException(
                rule="assignment_already_exists",
                message=f"An active assignment already exists for {classroom} - {school_year_level_subject.subject}.",
            )

        obj = TeacherAssignment(
            school_year_teacher=school_year_teacher,
            classroom=classroom,
            school_year_level_subject=school_year_level_subject,
            assignment_status=TeacherAssignmentStatus.ACTIVE,
            start_date=start_date,
        )
        obj.save_by(user=user)
        return obj

    @staticmethod
    def end(*, obj: TeacherAssignment, end_date: date, user=None) -> TeacherAssignment:
        """
        End an assignment (status → ENDED).
        
        Business rules:
        - Can only end ACTIVE assignments
        - end_date will be set automatically
        """
        if obj.assignment_status != TeacherAssignmentStatus.ACTIVE:
            raise BusinessRuleException(
                rule="assignment_not_active", 
                message="Only ACTIVE assignments can be ended.",
            )

        obj.assignment_status = TeacherAssignmentStatus.ENDED
        obj.end_date = end_date
        obj.save_by(user=user)
        return obj

    @staticmethod
    @transaction.atomic
    def replace(
        *,
        obj: TeacherAssignment,
        new_school_year_teacher,
        start_date: date,
        user=None,
    ) -> TeacherAssignment:
        """
        Replace a teacher assignment (old → REPLACED, new → ACTIVE).
        
        Business rules:
        - Can only replace ACTIVE assignments
        - new_teacher must be ACTIVE
        - New assignment for same (classroom, subject)
        - start_date becomes end_date for old assignment
        """
        if obj.assignment_status != TeacherAssignmentStatus.ACTIVE:
            raise BusinessRuleException(
                rule="assignment_not_active",
                message="Only ACTIVE assignments can be replaced.",
            )

        if new_school_year_teacher.status != SchoolYearTeacherStatus.ACTIVE:
            raise BusinessRuleException(
                rule="teacher_not_active",
                message=f"Replacement teacher {new_school_year_teacher.teacher} is not active.",
            )

        # Lock existing assignment to prevent concurrent modifications
        obj = TeacherAssignment.objects.select_for_update().get(id=obj.id)

        # End current assignment
        obj.assignment_status = TeacherAssignmentStatus.REPLACED
        obj.end_date = start_date
        obj.save_by(user=user)

        # Create new assignment
        new_assignment = TeacherAssignment(
            school_year_teacher=new_school_year_teacher,
            classroom=obj.classroom,
            school_year_level_subject=obj.school_year_level_subject,
            assignment_status=TeacherAssignmentStatus.ACTIVE,
            start_date=start_date,
        )
        new_assignment.save_by(user=user)

        # Link replacement
        obj.replaced_by = new_assignment
        obj.save_by(user=user)

        return new_assignment

    @staticmethod
    def update(
        *, obj: TeacherAssignment, start_date: date | None = None, user=None
    ) -> TeacherAssignment:
        """
        Update assignment dates (limited modifications).
        
        Only ACTIVE assignments can be updated.
        """
        if obj.assignment_status != TeacherAssignmentStatus.ACTIVE:
            raise BusinessRuleException(
                rule="assignment_not_active",
                message="Only ACTIVE assignments can be updated.",
            )

        if start_date is not None:
            obj.start_date = start_date

        obj.save_by(user=user)
        return obj

    @staticmethod
    def delete(*, obj: TeacherAssignment, user=None) -> TeacherAssignment:
        """Soft delete an assignment (should be rare in production)."""
        obj.soft_delete(user=user)
        return obj