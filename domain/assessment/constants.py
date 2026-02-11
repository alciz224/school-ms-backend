from django.db import models


class AssessmentStatus(models.TextChoices):
    """Status for Assessment (global evaluation framework)."""

    DRAFT = "DRAFT", "Draft"
    ACTIVE = "ACTIVE", "Active"
    CLOSED = "CLOSED", "Closed"
    ARCHIVED = "ARCHIVED", "Archived"


class AssessmentSubjectStatus(models.TextChoices):
    """Status for AssessmentSubject (specific exam/test for a subject+classroom)."""

    DRAFT = "DRAFT", "Draft"
    PUBLISHED = "PUBLISHED", "Published"
    CLOSED = "CLOSED", "Closed"
    ARCHIVED = "ARCHIVED", "Archived"


class StudentAssessmentStatus(models.TextChoices):
    """Status for StudentAssessment (individual student grade)."""

    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    VALIDATED = "VALIDATED", "Validated"
    CANCELLED = "CANCELLED", "Cancelled"


# Status transition maps
ASSESSMENT_STATUS_TRANSITIONS = {
    AssessmentStatus.DRAFT: [AssessmentStatus.ACTIVE],
    AssessmentStatus.ACTIVE: [AssessmentStatus.CLOSED],
    AssessmentStatus.CLOSED: [AssessmentStatus.ARCHIVED],
    AssessmentStatus.ARCHIVED: [],
}

ASSESSMENT_SUBJECT_STATUS_TRANSITIONS = {
    AssessmentSubjectStatus.DRAFT: [AssessmentSubjectStatus.PUBLISHED],
    AssessmentSubjectStatus.PUBLISHED: [AssessmentSubjectStatus.CLOSED],
    AssessmentSubjectStatus.CLOSED: [AssessmentSubjectStatus.ARCHIVED],
    AssessmentSubjectStatus.ARCHIVED: [],
}

STUDENT_ASSESSMENT_STATUS_TRANSITIONS = {
    StudentAssessmentStatus.DRAFT: [StudentAssessmentStatus.SUBMITTED, StudentAssessmentStatus.CANCELLED],
    StudentAssessmentStatus.SUBMITTED: [StudentAssessmentStatus.VALIDATED, StudentAssessmentStatus.CANCELLED],
    StudentAssessmentStatus.VALIDATED: [StudentAssessmentStatus.CANCELLED],
    StudentAssessmentStatus.CANCELLED: [],
}
