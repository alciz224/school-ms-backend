from django.db import models


class StudentEnrollmentStatus(models.TextChoices):
    PRE_REGISTERED = "PRE_REGISTERED", "Pre-registered"
    ACTIVE = "ACTIVE", "Active"
    COMPLETED = "COMPLETED", "Completed"
    DROPPED = "DROPPED", "Dropped"


class TeacherAssignmentStatus(models.TextChoices):
    """Status for teacher assignment to a classroom+subject."""
    
    ACTIVE = "ACTIVE", "Active"
    REPLACED = "REPLACED", "Replaced"
    ENDED = "ENDED", "Ended"