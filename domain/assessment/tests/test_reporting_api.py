import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from domain.account.models import CustomUser
from domain.academic.models import AssessmentType, Subject, Term
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus, StudentAssessmentStatus
from domain.assessment.models import Assessment, AssessmentSubject, StudentAssessment
from domain.enrollment.services import StudentEnrollmentService, TeacherAssignmentService
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import SchoolYearCycleTerm, SchoolYearLevelSubject, SchoolYearTeacher


def _login_with_role(client, user, role: str):
    client.force_login(user)
    session = client.session
    session["current_role"] = role
    session.save()


@pytest.mark.django_db
def test_report_card_generate_and_fetch_endpoints(client, school_year, school_year_level, classroom_a):
    # Minimal setup for speed
    staff = CustomUser.objects.create_user(email="staff@example.com", password="pass", first_name="S", last_name="A")
    _login_with_role(client, staff, role="STAFF")

    subj = Subject.objects.create(name="Math", code="MATH")
    syls = SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level,
        subject=subj,
        coefficient=Decimal("2.0"),
    )

    teacher = CustomUser.objects.create_user(email="t@example.com", password="pass", first_name="T", last_name="E")
    syt = SchoolYearTeacher.objects.create(
        school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE
    )
    # direct TeacherAssignment service (minimal validations)
    ta = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls,
        start_date=school_year.start_date,
    )

    term = Term.objects.create(term_type=school_year_level.school_year_cycle.term_type, name="T1", code="T1", order=1)
    term_period = SchoolYearCycleTerm.objects.create(
        school_year_cycle=school_year_level.school_year_cycle,
        term=term,
        start_date=school_year.start_date,
        end_date=school_year.start_date + datetime.timedelta(days=90),
    )

    at = AssessmentType.objects.create(name="Exam", code="EXAM")
    assessment = Assessment.objects.create(
        school_year=school_year,
        school_year_cycle=school_year_level.school_year_cycle,
        school_year_cycle_term=term_period,
        assessment_type=at,
        name="T1",
        status=AssessmentStatus.ACTIVE,
        start_date=term_period.start_date,
        end_date=term_period.end_date,
    )

    asub = AssessmentSubject.objects.create(
        assessment=assessment,
        classroom=classroom_a,
        school_year_level_subject=syls,
        teacher_assignment=ta,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )

    student = StudentEnrollmentService.create(
        student=None,
        first_name="A",
        last_name="One",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-RAPI-1",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    StudentAssessment.objects.create(
        assessment_subject=asub,
        student_enrollment=student,
        raw_score=Decimal("12.0"),
        status=StudentAssessmentStatus.VALIDATED,
    )

    gen_url = reverse("assessment:report-card-generate")
    resp = client.post(gen_url, data={
        "classroom_id": classroom_a.id,
        "term_id": term_period.id,
        "force": True,
    }, content_type="application/json")
    assert resp.status_code == 200

    rc_url = reverse("assessment:report-card-student-term", args=[student.id, term_period.id])
    resp2 = client.get(rc_url)
    assert resp2.status_code == 200
    assert resp2.json()["student_enrollment"] == student.id


@pytest.mark.django_db
def test_transcript_generate_and_fetch_endpoints(client, school_year, school_year_level, classroom_a):
    staff = CustomUser.objects.create_user(email="staff2@example.com", password="pass", first_name="S", last_name="B")
    _login_with_role(client, staff, role="STAFF")

    student = StudentEnrollmentService.create(
        student=None,
        first_name="B",
        last_name="Two",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-RAPI-2",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    # Create minimal report card to allow transcript generation
    from domain.assessment.models import ReportCard

    term = Term.objects.create(term_type=school_year_level.school_year_cycle.term_type, name="T1", code="T1", order=1)
    term_period = SchoolYearCycleTerm.objects.create(
        school_year_cycle=school_year_level.school_year_cycle,
        term=term,
        start_date=school_year.start_date,
        end_date=school_year.start_date + datetime.timedelta(days=90),
    )

    ReportCard.objects.create(
        student_enrollment=student,
        school_year_cycle_term=term_period,
        classroom=classroom_a,
        overall_average=Decimal("12.0"),
        rank=1,
        is_final=True,
    )

    gen_url = reverse("assessment:transcript-generate")
    r1 = client.post(gen_url, data={
        "student_enrollment_id": student.id,
        "school_year_id": school_year.id,
    }, content_type="application/json")
    assert r1.status_code == 200

    fetch_url = reverse("assessment:transcript-student-year", args=[student.id, school_year.id])
    r2 = client.get(fetch_url)
    assert r2.status_code == 200
    assert r2.json()["student_enrollment"] == student.id
