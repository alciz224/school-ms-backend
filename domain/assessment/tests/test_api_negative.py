import datetime
from decimal import Decimal

import pytest
from django.urls import reverse

from domain.account.models import CustomUser
from domain.academic.models import AssessmentType, Subject, Term, TermType
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus
from domain.assessment.models import Assessment, AssessmentSubject
from domain.enrollment.services import StudentEnrollmentService, TeacherAssignmentService
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import SchoolYearCycleTerm, SchoolYearLevelSubject, SchoolYearTeacher


def _login_with_role(client, user, role: str):
    client.force_login(user)
    session = client.session
    session["current_role"] = role
    session.save()


@pytest.mark.django_db
def test_api_commit_rejects_enrollment_not_in_classroom(client, school_year, school_year_level, classroom_a, classroom_b):
    teacher = CustomUser.objects.create_user(email="tt@example.com", password="pass", first_name="T", last_name="T")
    _login_with_role(client, teacher, role="TEACHER")

    subj = Subject.objects.create(name="Hist", code="HIS")
    syls = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subj, coefficient=Decimal("1.0"))

    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)
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
    assess = Assessment.objects.create(
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
        assessment=assess,
        classroom=classroom_a,
        school_year_level_subject=syls,
        teacher_assignment=ta,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )

    e_other = StudentEnrollmentService.create(
        student=None,
        first_name="N",
        last_name="ClassB",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-B",
        classroom=classroom_b,
        enrollment_status="ACTIVE",
    )

    commit_url = reverse("assessment:assessment-subject-grades-commit", args=[asub.id])
    r = client.post(commit_url, data={
        "grades": [{"enrollment_id": e_other.id, "raw_score": "10.0"}]
    }, content_type="application/json")

    assert r.status_code in (400, 422)
