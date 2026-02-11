"""AssessmentSubject model (Assessment domain)."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from domain.assessment.constants import (
    AssessmentSubjectStatus,
    ASSESSMENT_SUBJECT_STATUS_TRANSITIONS,
)
from domain.assessment.models.assessment import Assessment
from domain.enrollment.models import Classroom, TeacherAssignment
from domain.school_operations.models import SchoolYearLevelSubject
from domain.shared.models.base import AuditModel


class AssessmentSubject(AuditModel):
    """
    Concrete examination/test for a specific subject in a specific classroom.
    
    Represents the actual exam that students will take (e.g., "Math Exam for 6eA").
    
    Business Rules:
        - Unique per (assessment, classroom, school_year_level_subject)
        - Only one exam per subject/classroom for an assessment
        - Can only be created when Assessment is ACTIVE
        - teacher_assignment must be ACTIVE and match (classroom, subject)
        - Classroom and SchoolYearLevelSubject must be coherent
        - Status workflow: DRAFT → PUBLISHED → CLOSED → ARCHIVED
        - StudentAssessment can only be created when status is PUBLISHED
    """

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.PROTECT,
        related_name="assessment_subjects",
        help_text="Parent assessment framework",
    )
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.PROTECT,
        related_name="assessment_subjects",
        help_text="Classroom taking this exam",
    )
    school_year_level_subject = models.ForeignKey(
        SchoolYearLevelSubject,
        on_delete=models.PROTECT,
        related_name="assessment_subjects", 
        help_text="Subject + coefficient for the level",
    )
    teacher_assignment = models.ForeignKey(
        TeacherAssignment,
        on_delete=models.PROTECT,
        related_name="assessment_subjects",
        help_text="Teacher responsible for this exam (frozen at creation)",
    )
    
    status = models.CharField(
        max_length=20,
        choices=AssessmentSubjectStatus.choices,
        default=AssessmentSubjectStatus.DRAFT,
        help_text="Status of the assessment subject",
    )
    
    max_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        help_text="Maximum possible score for this exam",
    )
    
    instructions = models.TextField(
        blank=True,
        help_text="Instructions or notes for this specific exam",
    )

    class Meta:
        db_table = "assessment_subject"
        verbose_name = "Assessment Subject"
        verbose_name_plural = "Assessment Subjects"
        ordering = ["assessment", "classroom", "school_year_level_subject"]
        indexes = [
            models.Index(
                fields=["assessment", "classroom", "school_year_level_subject"],
                name="ass_subj_acls_subj_idx",
            ),
            models.Index(fields=["teacher_assignment"], name="assess_subj_teacher_idx"),
            models.Index(fields=["status"], name="assess_subj_status_idx"),
        ]
        constraints = [
            # Unique exam per assessment/classroom/subject
            models.UniqueConstraint(
                fields=["assessment", "classroom", "school_year_level_subject"],
                condition=models.Q(is_deleted=False),
                name="unique_assessment_subject_per_assessment_classroom_subject",
            ),
            # Max score must be positive
            models.CheckConstraint(
                condition=models.Q(max_score__gt=0),
                name="assessment_subject_max_score_positive",
            ),
        ]

    def __str__(self) -> str:
        subject_name = self.school_year_level_subject.subject.name
        classroom_name = self.classroom.name
        return f"{self.assessment.name} - {subject_name} ({classroom_name}) [{self.status}]"

    def clean(self):
        super().clean()

        # Can only create when parent Assessment is ACTIVE
        if self.assessment_id and self.assessment.status != "ACTIVE":
            raise ValidationError({
                "assessment": "Assessment must be ACTIVE to create subjects."
            })

        # Coherence: classroom.school_year_level == school_year_level_subject.school_year_level
        if self.classroom_id and self.school_year_level_subject_id:
            if self.classroom.school_year_level_id != self.school_year_level_subject.school_year_level_id:
                raise ValidationError({
                    "school_year_level_subject": 
                    "Subject must belong to the same SchoolYearLevel as the classroom."
                })

        # Coherence: teacher_assignment must match classroom + subject and be ACTIVE
        if self.teacher_assignment_id and self.classroom_id and self.school_year_level_subject_id:
            ta = self.teacher_assignment
            if not ta.is_active:
                raise ValidationError({
                    "teacher_assignment": "Teacher assignment must be ACTIVE."
                })
            if ta.classroom_id != self.classroom_id:
                raise ValidationError({
                    "teacher_assignment": "Teacher assignment must be for the same classroom."
                })
            if ta.school_year_level_subject_id != self.school_year_level_subject_id:
                raise ValidationError({
                    "teacher_assignment": "Teacher assignment must be for the same subject."
                })

        # Coherence: assessment.school_year must match classroom's school_year
        if self.assessment_id and self.classroom_id:
            assessment_school_year_id = self.assessment.school_year_id
            classroom_school_year_id = self.classroom.school_year_level.school_year_cycle.school_year_id
            if assessment_school_year_id != classroom_school_year_id:
                raise ValidationError({
                    "classroom": "Classroom must belong to the same school year as the assessment."
                })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition to new status is allowed."""
        allowed_transitions = ASSESSMENT_SUBJECT_STATUS_TRANSITIONS.get(self.status, [])
        return new_status in allowed_transitions

    @property
    def is_published(self) -> bool:
        """Check if assessment subject is published."""
        return self.status == AssessmentSubjectStatus.PUBLISHED and not self.is_deleted

    @property
    def can_accept_grades(self) -> bool:
        """Check if new StudentAssessment can be created."""
        return self.is_published

    @property
    def is_closed_or_archived(self) -> bool:
        """Check if assessment subject is closed or archived."""
        return self.status in [AssessmentSubjectStatus.CLOSED, AssessmentSubjectStatus.ARCHIVED]

    @property
    def teacher(self):
        """Shortcut to access the teacher."""
        return self.teacher_assignment.teacher

    @property
    def subject(self):
        """Shortcut to access the subject."""
        return self.school_year_level_subject.subject

    @property
    def school_year_level(self):
        """Shortcut to access the school year level."""
        return self.school_year_level_subject.school_year_level