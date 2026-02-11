import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from domain.account.models import CustomUser
from domain.academic.models import Subject, Term, TermType
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus
from domain.assessment.models import Assessment, AssessmentSubject
from domain.enrollment.services import StudentEnrollmentService, TeacherAssignmentService
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import (
    SchoolYearCycle,
    SchoolYearCycleTerm,
    SchoolYearLevelSubject,
    SchoolYearTeacher,
)


def _login_with_role(client, user, role: str):
    client.force_login(user)
    # Ensure session has current_role per project permission pattern
    session = client.session
    session["current_role"] = role
    session.save()


@pytest.mark.django_db
def test_bulk_preview_and_commit_endpoints_teacher(client, school_year, school_year_level, classroom_a):
    # Teacher and assignment setup
    teacher = CustomUser.objects.create_user(email="teach@example.com", password="pass", first_name="Teach", last_name="Er")
    _login_with_role(client, teacher, role="TEACHER")

    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)

    subject = Subject.objects.create(name="Math", code="MATH")
    syls = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subject, coefficient=Decimal("2.0"))

    ta = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls,
        start_date=school_year.start_date,
    )

    # Assessment and subject (published)
    term_type = school_year_level.school_year_cycle.term_type
    t1 = Term.objects.create(term_type=term_type, name="T1", code="T1", order=1)
    syct = SchoolYearCycleTerm.objects.create(
        school_year_cycle=school_year_level.school_year_cycle,
        term=t1,
        start_date=school_year.start_date,
        end_date=school_year.start_date + datetime.timedelta(days=90),
    )

    from domain.academic.models import AssessmentType as AT
    at = AT.objects.create(name="Exam", code="EXAM")
    assess = Assessment.objects.create(
        school_year=school_year,
        school_year_cycle=school_year_level.school_year_cycle,
        school_year_cycle_term=syct,
        assessment_type=at,
        name="T1 Exams",
        status=AssessmentStatus.ACTIVE,
        start_date=syct.start_date,
        end_date=syct.end_date,
    )

    asub = AssessmentSubject.objects.create(
        assessment=assess,
        classroom=classroom_a,
        school_year_level_subject=syls,
        teacher_assignment=ta,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )

    # Two enrollments
    e1 = StudentEnrollmentService.create(
        student=None,
        first_name="A",
        last_name="One",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-TAPI-1",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )
    e2 = StudentEnrollmentService.create(
        student=None,
        first_name="B",
        last_name="Two",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-TAPI-2",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    # Preview OK
    preview_url = reverse("assessment:assessment-subject-grades-preview", args=[asub.id])
    resp = client.post(preview_url, data={
        "grades": [
            {"enrollment_id": e1.id, "raw_score": "15.0"},
            {"enrollment_id": e2.id, "raw_score": "18.0"},
        ]
    }, content_type="application/json")
    assert resp.status_code == 200
    assert resp.json()["creates"] == 2

    # Commit OK
    commit_url = reverse("assessment:assessment-subject-grades-commit", args=[asub.id])
    resp2 = client.post(commit_url, data={
        "grades": [
            {"enrollment_id": e1.id, "raw_score": "15.0"},
            {"enrollment_id": e2.id, "raw_score": "18.0"},
        ]
    }, content_type="application/json")
    assert resp2.status_code == 200
    body = resp2.json()
    assert body["created"] == 2 and body["total"] == 2

    # Invalid: absent with score
    resp3 = client.post(commit_url, data={
        "grades": [
            {"enrollment_id": e1.id, "raw_score": None, "is_absent": True},
            {"enrollment_id": e2.id, "raw_score": "5.0", "is_absent": True}
        ]
    }, content_type="application/json")
    assert resp3.status_code in (400, 422)
    body3 = resp3.json()
    # Structured error present (wrapped under 'error')
    assert body3.get("error", {}).get("code") in ("absent_with_score", "validation_error")
    assert body3.get("error", {}).get("details", {}).get("error", {}).get("index") == 1


@pytest.mark.django_db
def test_bulk_commit_all_or_nothing_invalid_input_returns_400(client, school_year, school_year_level, classroom_a):
    teacher = CustomUser.objects.create_user(email="teach2@example.com", password="pass")
    _login_with_role(client, teacher, role="TEACHER")

    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)
    subject = Subject.objects.create(name="Fr", code="FR")
    syls = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subject, coefficient=Decimal("1.0"))
    ta = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls,
        start_date=school_year.start_date,
    )
    term_type = school_year_level.school_year_cycle.term_type
    t1 = Term.objects.create(term_type=term_type, name="T1", code="T1", order=1)
    syct = SchoolYearCycleTerm.objects.create(
        school_year_cycle=school_year_level.school_year_cycle,
        term=t1,
        start_date=school_year.start_date,
        end_date=school_year.start_date + datetime.timedelta(days=90),
    )
    assess = Assessment.objects.create(
        school_year=school_year,
        school_year_cycle=school_year_level.school_year_cycle,
        school_year_cycle_term=syct,
        assessment_type=None,
        name="T1",
        status=AssessmentStatus.ACTIVE,
        start_date=syct.start_date,
        end_date=syct.end_date,
    )
    asub = AssessmentSubject.objects.create(
        assessment=assess,
        classroom=classroom_a,
        school_year_level_subject=syls,
        teacher_assignment=ta,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )

    e1 = StudentEnrollmentService.create(
        student=None,
        first_name="C",
        last_name="Three",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-TAPI-3",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    commit_url = reverse("assessment:assessment-subject-grades-commit", args=[asub.id])
    # invalid: score beyond max -> should be 400
    resp = client.post(commit_url, data={
        "grades": [
            {"enrollment_id": e1.id, "raw_score": "25.0"}
        ]
    }, content_type="application/json")
    assert resp.status_code in (400, 422)


@pytest.mark.django_db
def test_permissions_non_teacher_cannot_commit(client, school_year, school_year_level, classroom_a):
    # Login as STUDENT
    user = CustomUser.objects.create_user(email="student@example.com", password="pass")
    _login_with_role(client, user, role="STUDENT")

    # Try to hit commit endpoint (any id)
    url = reverse("assessment:assessment-subject-grades-commit", args=[12345])
    resp = client.post(url, data={"grades": []}, content_type="application/json")
    # DRF permission classes should deny
    assert resp.status_code == 403


@pytest.mark.django_db
def test_read_endpoints_teacher_and_student(client, school_year, school_year_level, classroom_a):
    teacher = CustomUser.objects.create_user(email="t3@example.com", password="pass")
    _login_with_role(client, teacher, role="TEACHER")

    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)
    subject = Subject.objects.create(name="Sci", code="SCI")
    syls = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subject, coefficient=Decimal("1.0"))
    ta = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls,
        start_date=school_year.start_date,
    )
    term_type = school_year_level.school_year_cycle.term_type
    t1 = Term.objects.create(term_type=term_type, name="T1", code="T1", order=1)
    syct = SchoolYearCycleTerm.objects.create(
        school_year_cycle=school_year_level.school_year_cycle,
        term=t1,
        start_date=school_year.start_date,
        end_date=school_year.start_date + datetime.timedelta(days=90),
    )
    assess = Assessment.objects.create(
        school_year=school_year,
        school_year_cycle=school_year_level.school_year_cycle,
        school_year_cycle_term=syct,
        assessment_type=None,
        name="T1",
        status=AssessmentStatus.ACTIVE,
        start_date=syct.start_date,
        end_date=syct.end_date,
    )
    asub = AssessmentSubject.objects.create(
        assessment=assess,
        classroom=classroom_a,
        school_year_level_subject=syls,
        teacher_assignment=ta,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )

    # Teacher: grading sheet
    grading_sheet_url = reverse("assessment:assessment-subject-grading-sheet", args=[asub.id])
    r1 = client.get(grading_sheet_url)
    assert r1.status_code == 200

    # Student grades history: as STUDENT allowed

    # Switch to STUDENT for own grades history (no data yet, but endpoint accessible)
    student_user = CustomUser.objects.create_user(email="stu@example.com", password="pass")
    _login_with_role(client, student_user, role="STUDENT")
    # No enrollment id available here; just verify permission wiring blocks teacher-only routes now
    r2 = client.get(grading_sheet_url)
    assert r2.status_code == 403
