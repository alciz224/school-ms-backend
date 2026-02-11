"""StudentAssessment model (Assessment domain)."""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import models

from domain.assessment.constants import (
    StudentAssessmentStatus,
    STUDENT_ASSESSMENT_STATUS_TRANSITIONS,
)
from domain.assessment.models.assessment_subject import AssessmentSubject
from domain.enrollment.models import StudentEnrollment
from domain.shared.models.base import AuditModel


class StudentAssessment(AuditModel):
    """
    Individual grade for a student in a specific assessment subject.
    
    Represents the actual grade/score a student received (e.g., "15/20 for Mamadou in Math Exam").
    
    Business Rules:
        - Unique per (assessment_subject, student_enrollment)
        - Only one grade per student per exam
        - Can only be created when AssessmentSubject is PUBLISHED
        - Student must be enrolled in the same classroom as the assessment
        - 0 <= raw_score <= max_score (when not absent)
        - If absent: raw_score must be NULL
        - Status workflow: DRAFT → SUBMITTED → VALIDATED → CANCELLED
        - Validated scores can be modified until AssessmentSubject is CLOSED
    """

    assessment_subject = models.ForeignKey(
        AssessmentSubject,
        on_delete=models.PROTECT,
        related_name="student_assessments",
        help_text="The exam this grade belongs to",
    )
    student_enrollment = models.ForeignKey(
        StudentEnrollment,
        on_delete=models.PROTECT,
        related_name="student_assessments",
        help_text="Student enrollment (must be in same classroom)",
    )
    
    raw_score = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Score obtained by the student (NULL if absent)",
    )
    
    is_absent = models.BooleanField(
        default=False,
        help_text="Student was absent for this assessment",
    )
    is_excused = models.BooleanField(
        default=False,
        help_text="Absence was excused",
    )
    
    status = models.CharField(
        max_length=20,
        choices=StudentAssessmentStatus.choices,
        default=StudentAssessmentStatus.DRAFT,
        help_text="Status of this grade",
    )
    
    remark = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional teacher comment/remark",
    )

    class Meta:
        db_table = "student_assessment"
        verbose_name = "Student Assessment"
        verbose_name_plural = "Student Assessments"
        ordering = ["assessment_subject", "student_enrollment"]
        indexes = [
            models.Index(
                fields=["assessment_subject", "student_enrollment"],
                name="stud_assess_subj_enroll_idx",
            ),
            models.Index(fields=["status"], name="stud_assess_status_idx"),
            models.Index(fields=["is_absent", "is_excused"], name="stud_assess_absence_idx"),
        ]
        constraints = [
            # Unique grade per student per exam
            models.UniqueConstraint(
                fields=["assessment_subject", "student_enrollment"],
                condition=models.Q(is_deleted=False),
                name="unique_student_assessment_per_subject_enrollment",
            ),
            # Score bounds validation (when not absent)
            models.CheckConstraint(
                condition=models.Q(is_absent=True, raw_score__isnull=True) |
                          models.Q(is_absent=False, raw_score__gte=0),
                name="student_assessment_score_bounds",
            ),
        ]

    def __str__(self) -> str:
        student_name = self.student_enrollment.display_name
        subject_name = self.assessment_subject.subject.name
        if self.is_absent:
            score_display = "Absent"
        elif self.raw_score is not None:
            score_display = f"{self.raw_score}/{self.assessment_subject.max_score}"
        else:
            score_display = "No score"
        return f"{student_name} - {subject_name}: {score_display} [{self.status}]"

    def clean(self):
        super().clean()

        # Can only create when AssessmentSubject is PUBLISHED
        if self.assessment_subject_id and not self.assessment_subject.can_accept_grades:
            raise ValidationError({
                "assessment_subject": "Assessment subject must be PUBLISHED to accept grades."
            })

        # Student must be enrolled in the same classroom
        if self.assessment_subject_id and self.student_enrollment_id:
            if self.student_enrollment.classroom_id != self.assessment_subject.classroom_id:
                raise ValidationError({
                    "student_enrollment": "Student must be enrolled in the same classroom as the assessment."
                })

        # Absence logic
        if self.is_absent and self.raw_score is not None:
            raise ValidationError({
                "raw_score": "Score must be NULL when student is absent."
            })

        # Score bounds (when not absent)
        if not self.is_absent and self.raw_score is not None:
            if self.raw_score < 0:
                raise ValidationError({
                    "raw_score": "Score cannot be negative."
                })
            if self.assessment_subject_id and self.raw_score > self.assessment_subject.max_score:
                raise ValidationError({
                    "raw_score": f"Score cannot exceed maximum score ({self.assessment_subject.max_score})."
                })

        # Status validation: cannot validate absent scores
        if self.is_absent and self.status == StudentAssessmentStatus.VALIDATED:
            raise ValidationError({
                "status": "Cannot validate grades for absent students."
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def can_transition_to(self, new_status: str) -> bool:
        """Check if transition to new status is allowed."""
        allowed_transitions = STUDENT_ASSESSMENT_STATUS_TRANSITIONS.get(self.status, [])
        return new_status in allowed_transitions

    @property
    def is_validated(self) -> bool:
        """Check if assessment is validated."""
        return self.status == StudentAssessmentStatus.VALIDATED and not self.is_deleted

    @property
    def can_be_modified(self) -> bool:
        """Check if grade can still be modified."""
        # Can modify until AssessmentSubject is closed
        return not self.assessment_subject.is_closed_or_archived

    @property
    def counts_for_average(self) -> bool:
        """Check if this grade should count towards average calculation."""
        # Validated scores that are not absent count towards average
        return self.is_validated and not self.is_absent

    @property
    def display_score(self) -> str:
        """Human-readable score display."""
        if self.is_absent:
            return "Absent" if not self.is_excused else "Absent (Excused)"
        elif self.raw_score is not None:
            return f"{self.raw_score}/{self.assessment_subject.max_score}"
        else:
            return "No score"

    @property
    def student(self):
        """Shortcut to access the student."""
        return self.student_enrollment.student

    @property
    def subject(self):
        """Shortcut to access the subject."""
        return self.assessment_subject.subject