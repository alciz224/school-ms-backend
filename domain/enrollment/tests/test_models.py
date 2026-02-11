import datetime

import pytest
from django.core.exceptions import ValidationError

from domain.enrollment.models import Classroom, StudentEnrollment, StudentEnrollmentStatus


@pytest.mark.django_db
def test_classroom_unique_per_school_year_level(school_year_level):
    Classroom.objects.create(school_year_level=school_year_level, name="A")

    with pytest.raises(ValidationError):
        Classroom.objects.create(school_year_level=school_year_level, name="A")


@pytest.mark.django_db
def test_student_enrollment_date_validation(student, school_year_level):
    enrollment = StudentEnrollment(
        student=None,
        first_name="A",
        last_name="B",
        school_year_level=school_year_level,
        enrollment_date=datetime.date(2025, 9, 10),
        start_date=datetime.date(2025, 9, 1),
        annual_identifier="AY-1",
        enrollment_status=StudentEnrollmentStatus.PRE_REGISTERED,
    )

    with pytest.raises(ValidationError):
        enrollment.full_clean()
