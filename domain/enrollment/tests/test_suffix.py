import datetime

import pytest

from domain.enrollment.services import StudentEnrollmentService


@pytest.mark.django_db
def test_suffix_assigned_only_on_collision(student, school_year_level, classroom_a):
    e1 = StudentEnrollmentService.create(
        student=None,
        first_name="Mamadou",
        last_name="Diallo",
        school_year_level=school_year_level,
        enrollment_date=datetime.date(2025, 9, 1),
        annual_identifier="AY-100",
        classroom=classroom_a,
    )
    assert e1.classroom_suffix is None
    assert e1.display_name == "Mamadou Diallo"

    e2 = StudentEnrollmentService.create(
        student=None,
        first_name="Mamadou",
        last_name="Diallo",
        school_year_level=school_year_level,
        enrollment_date=datetime.date(2025, 9, 1),
        annual_identifier="AY-101",
        classroom=classroom_a,
    )

    # collision => first becomes 1 and second becomes 2
    e1.refresh_from_db()
    assert e1.classroom_suffix == 1
    assert e1.display_name == "Mamadou 1 Diallo"

    assert e2.classroom_suffix == 2
    assert e2.display_name == "Mamadou 2 Diallo"
