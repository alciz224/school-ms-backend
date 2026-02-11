"""TeacherAssignment model (Enrollment domain)."""

from django.core.exceptions import ValidationError
from django.db import models

from domain.enrollment.constants import TeacherAssignmentStatus
from domain.enrollment.models.classroom import Classroom
from domain.school_operations.models import SchoolYearLevelSubject, SchoolYearTeacher
from domain.shared.models.base import AuditModel


class TeacherAssignment(AuditModel):
    """
    Assignment of a teacher to teach a specific subject in a specific classroom.
    
    Business Rules:
        - Only one ACTIVE assignment per (classroom, school_year_level_subject) at a time
        - school_year_teacher must have status ACTIVE to create new assignments
        - classroom.school_year_level must match school_year_level_subject.school_year_level
        - school_year_teacher.school_year must be parent of the school_year_level
        - start_date must be within school year period
        - end_date required if status is REPLACED or ENDED
        - replaced_by can only point to assignment for same (classroom, subject)
        
    Workflow:
        - Create: status=ACTIVE, start_date required
        - End: status=ENDED, end_date required
        - Replace: old → REPLACED+end_date, new → ACTIVE+start_date
    """

    school_year_teacher = models.ForeignKey(
        SchoolYearTeacher,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
        help_text="Teacher assigned to school year (prerequisite)",
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
        help_text="Classroom where teaching occurs",
    )
    school_year_level_subject = models.ForeignKey(
        SchoolYearLevelSubject,
        on_delete=models.PROTECT,
        related_name="teacher_assignments",
        help_text="Subject + coefficient for the level",
    )
    assignment_status = models.CharField(
        max_length=20,
        choices=TeacherAssignmentStatus.choices,
        default=TeacherAssignmentStatus.ACTIVE,
        help_text="Status of the assignment",
    )
    start_date = models.DateField(
        help_text="Start date of the assignment",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="End date (required if REPLACED or ENDED)",
    )
    replaced_by = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        related_name="replaces",
        null=True,
        blank=True,
        help_text="Assignment that replaces this one",
    )

    class Meta:
        db_table = "teacher_assignment"
        verbose_name = "Teacher Assignment"
        verbose_name_plural = "Teacher Assignments"
        ordering = ["classroom", "school_year_level_subject", "-start_date"]
        indexes = [
            models.Index(
                fields=["classroom", "school_year_level_subject", "assignment_status"],
                name="teacher_assign_cls_subj_idx",
            ),
            models.Index(fields=["school_year_teacher"], name="teacher_assign_teacher_idx"),
            models.Index(fields=["start_date", "end_date"], name="teacher_assign_dates_idx"),
        ]
        constraints = [
            # Only one ACTIVE assignment per (classroom, subject)
            models.UniqueConstraint(
                fields=["classroom", "school_year_level_subject"],
                condition=models.Q(assignment_status=TeacherAssignmentStatus.ACTIVE, is_deleted=False),
                name="unique_active_teacher_assignment",
            ),
            # end_date required if not ACTIVE
            models.CheckConstraint(
                condition=models.Q(assignment_status=TeacherAssignmentStatus.ACTIVE)
                | models.Q(end_date__isnull=False),
                name="teacher_assignment_end_date_required_if_not_active",
            ),
            # Dates coherence
            models.CheckConstraint(
                condition=models.Q(end_date__isnull=True) | models.Q(start_date__lt=models.F("end_date")),
                name="teacher_assignment_dates_coherent",
            ),
        ]

    def __str__(self) -> str:
        subject_name = self.school_year_level_subject.subject.name
        classroom_name = self.classroom.name
        teacher_name = f"{self.school_year_teacher.teacher.first_name} {self.school_year_teacher.teacher.last_name}"
        return f"{teacher_name} → {subject_name} ({classroom_name}) [{self.assignment_status}]"

    def clean(self):
        super().clean()

        # end_date required if not ACTIVE
        if self.assignment_status != TeacherAssignmentStatus.ACTIVE and not self.end_date:
            raise ValidationError({
                "end_date": f"End date is required when status is {self.assignment_status}."
            })

        # Dates coherence
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError({"end_date": "End date must be after start date."})

        # Coherence: classroom.school_year_level == school_year_level_subject.school_year_level
        if self.classroom_id and self.school_year_level_subject_id:
            if self.classroom.school_year_level_id != self.school_year_level_subject.school_year_level_id:
                raise ValidationError({
                    "school_year_level_subject": 
                    "Subject must belong to the same SchoolYearLevel as the classroom."
                })

        # Coherence: school_year_teacher.school_year must be parent of school_year_level
        if self.school_year_teacher_id and self.classroom_id:
            classroom_school_year_id = self.classroom.school_year_level.school_year_cycle.school_year_id
            if self.school_year_teacher.school_year_id != classroom_school_year_id:
                raise ValidationError({
                    "school_year_teacher": 
                    "Teacher must be assigned to the same school year as the classroom."
                })

        # Dates must fall within school year period
        if self.school_year_teacher_id and self.start_date:
            school_year = self.school_year_teacher.school_year
            if self.start_date < school_year.start_date or self.start_date > school_year.end_date:
                raise ValidationError({
                    "start_date": "Start date must fall within the school year period."
                })
            if self.end_date and (self.end_date < school_year.start_date or self.end_date > school_year.end_date):
                raise ValidationError({
                    "end_date": "End date must fall within the school year period."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    @property
    def is_active(self) -> bool:
        """Check if assignment is currently active."""
        return self.assignment_status == TeacherAssignmentStatus.ACTIVE and not self.is_deleted

    @property
    def teacher(self):
        """Shortcut to access the teacher user."""
        return self.school_year_teacher.teacher

    @property
    def subject(self):
        """Shortcut to access the subject."""
        return self.school_year_level_subject.subject

    @property
    def school_year_level(self):
        """Shortcut to access the school year level."""
        return self.school_year_level_subject.school_year_level