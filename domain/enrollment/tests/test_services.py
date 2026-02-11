import datetime

import pytest

from domain.enrollment.models import StudentEnrollmentStatus
from domain.enrollment.services import StudentEnrollmentService


@pytest.mark.django_db
def test_transfer_pre_registered_becomes_active(
    student,
    school_year_level,
    classroom_a,
    classroom_b,
):
    enrollment = StudentEnrollmentService.create(
        student=None,
        first_name="Mamadou",
        last_name="Diallo",
        school_year_level=school_year_level,
        enrollment_date=datetime.date(2025, 9, 1),
        annual_identifier="AY-2",
        classroom=classroom_a,
        enrollment_status=StudentEnrollmentStatus.PRE_REGISTERED,
    )

    assert enrollment.enrollment_status == StudentEnrollmentStatus.PRE_REGISTERED

    transferred = StudentEnrollmentService.transfer(
        obj=enrollment,
        to_classroom=classroom_b,
        transfer_date=datetime.date(2025, 9, 10),
        transfer_reason="Move",
        classroom_identifier="C-10",
    )

    assert transferred.classroom_id == classroom_b.id
    assert transferred.previous_classroom_id == classroom_a.id
    assert transferred.enrollment_status == StudentEnrollmentStatus.ACTIVE
    assert transferred.classroom_identifier == "C-10"
