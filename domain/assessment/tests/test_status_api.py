import datetime
import pytest
from django.urls import reverse
from decimal import Decimal

from domain.account.models import CustomUser
from domain.academic.models import AssessmentType, Subject, Term, TermType
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus
from domain.assessment.models import Assessment, AssessmentSubject
from domain.enrollment.services import TeacherAssignmentService
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import SchoolYearCycleTerm, SchoolYearLevelSubject, SchoolYearTeacher


def _login_with_role(client, user, role: str):
    client.force_login(user)
    session = client.session
    session["current_role"] = role
    session.save()


@pytest.mark.django_db
def test_assessment_status_http_endpoints_staff_only(client, school_year, school_year_level, classroom_a):
    # Login as STAFF
    staff = CustomUser.objects.create_user(email="staff@example.com", password="pass")
    _login_with_role(client, staff, role="STAFF")

    term_type = school_year_level.school_year_cycle.term_type
    t1 = Term.objects.create(term_type=term_type, name="T1", code="T1", order=1)
    syct = SchoolYearCycleTerm.objects.create(
        school_year_cycle=school_year_level.school_year_cycle,
        term=t1,
        start_date=school_year.start_date,
        end_date=school_year.start_date + datetime.timedelta(days=90),
    )
    at = AssessmentType.objects.create(name="Exam", code="EXAM")
    a = Assessment.objects.create(
        school_year=school_year,
        school_year_cycle=school_year_level.school_year_cycle,
        school_year_cycle_term=syct,
        assessment_type=at,
        name="T1",
        status=AssessmentStatus.DRAFT,
        start_date=syct.start_date,
        end_date=syct.end_date,
    )

    # Activate
    url_activate = reverse("assessment:assessment-status", args=[a.id, "activate"])
    r1 = client.post(url_activate)
    assert r1.status_code == 200 and r1.json()["status"] == AssessmentStatus.ACTIVE

    # Close
    url_close = reverse("assessment:assessment-status", args=[a.id, "close"])
    r2 = client.post(url_close)
    assert r2.status_code == 200 and r2.json()["status"] == AssessmentStatus.CLOSED

    # Teacher should be forbidden
    teacher = CustomUser.objects.create_user(email="t@example.com", password="pass")
    _login_with_role(client, teacher, role="TEACHER")
    r3 = client.post(url_activate)
    assert r3.status_code == 403


@pytest.mark.django_db
def test_assessment_subject_status_http_endpoints_staff_only(client, school_year, school_year_level, classroom_a):
    staff = CustomUser.objects.create_user(email="staff2@example.com", password="pass")
    _login_with_role(client, staff, role="STAFF")

    # Setup teacher assignment and subject
    subj = Subject.objects.create(name="Math", code="MATH")
    syls = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subj, coefficient=Decimal("1"))
    teacher_user = CustomUser.objects.create_user(email="t2@example.com", password="pass")
    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher_user, status=SchoolYearTeacherStatus.ACTIVE)
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
    at = AssessmentType.objects.create(name="Exam", code="EXAM")
    a = Assessment.objects.create(
        school_year=school_year,
        school_year_cycle=school_year_level.school_year_cycle,
        school_year_cycle_term=syct,
        assessment_type=at,
        name="T1",
        status=AssessmentStatus.ACTIVE,
        start_date=syct.start_date,
        end_date=syct.end_date,
    )

    asub = AssessmentSubject.objects.create(
        assessment=a,
        classroom=classroom_a,
        school_year_level_subject=syls,
        teacher_assignment=ta,
        status=AssessmentSubjectStatus.DRAFT,
        max_score=Decimal("20"),
    )

    # Publish
    url_publish = reverse("assessment:assessment-subject-status", args=[asub.id, "publish"])
    r1 = client.post(url_publish)
    assert r1.status_code == 200 and r1.json()["status"] == AssessmentSubjectStatus.PUBLISHED

    # Close
    url_close = reverse("assessment:assessment-subject-status", args=[asub.id, "close"])
    r2 = client.post(url_close)
    assert r2.status_code == 200 and r2.json()["status"] == AssessmentSubjectStatus.CLOSED

    # Teacher forbidden
    teacher = CustomUser.objects.create_user(email="t3@example.com", password="pass")
    _login_with_role(client, teacher, role="TEACHER")
    r3 = client.post(url_publish)
    assert r3.status_code == 403
