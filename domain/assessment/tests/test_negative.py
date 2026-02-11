import datetime
from decimal import Decimal

import pytest

from domain.account.models import CustomUser
from domain.academic.models import AssessmentType, Subject, Term, TermType
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus
from domain.assessment.models import Assessment, AssessmentSubject
from domain.assessment.services import StudentAssessmentService
from domain.enrollment.services import StudentEnrollmentService, TeacherAssignmentService
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import SchoolYearCycleTerm, SchoolYearLevelSubject, SchoolYearTeacher
from domain.shared.exceptions import ValidationException


@pytest.mark.django_db
def test_bulk_preview_and_commit_rejects_enrollment_not_in_classroom(school_year, school_year_level, classroom_a, classroom_b):
    # Setup subject + teacher assignment for classroom A
    subj = Subject.objects.create(name="Math", code="MATH")
    syls = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subj, coefficient=Decimal("1.0"))
    teacher = CustomUser.objects.create_user(email="ta@example.com", password="pass", first_name="T", last_name="A")
    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)
    ta = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls,
        start_date=school_year.start_date,
    )

    # Assessment/subject PUBLISHED
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

    # Enrollment in different classroom B
    e_other = StudentEnrollmentService.create(
        student=None,
        first_name="X",
        last_name="Else",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-NOTINCLASS",
        classroom=classroom_b,
        enrollment_status="ACTIVE",
    )

    # Preview should report error
    preview = StudentAssessmentService.preview_bulk_import(
        assessment_subject_id=asub.id,
        grades=[{"enrollment_id": e_other.id, "raw_score": Decimal("10.0")},],
    )
    assert preview["errors"] and preview["errors"][0]["code"] == "not_in_classroom" and preview["errors"][0]["enrollment_id"] == e_other.id

    # Commit should raise ValidationException
    with pytest.raises(ValidationException):
        StudentAssessmentService.commit_bulk_import(
            assessment_subject_id=asub.id,
            grades=[{"enrollment_id": e_other.id, "raw_score": Decimal("10.0")}],
        )


@pytest.mark.django_db
def test_bulk_preview_and_commit_rejects_missing_fields_and_bounds(school_year, school_year_level, classroom_a):
    subj = Subject.objects.create(name="Fr", code="FR")
    syls = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subj, coefficient=Decimal("1.0"))
    teacher = CustomUser.objects.create_user(email="tb@example.com", password="pass", first_name="T", last_name="B")
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

    # Create one enrollment
    e1 = StudentEnrollmentService.create(
        student=None,
        first_name="M",
        last_name="One",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-M1",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    # Missing enrollment_id
    preview1 = StudentAssessmentService.preview_bulk_import(
        assessment_subject_id=asub.id,
        grades=[{"raw_score": Decimal("12.0")}],
    )
    assert preview1["errors"] and preview1["errors"][0]["code"] == "missing_enrollment_id"

    # Negative score
    preview2 = StudentAssessmentService.preview_bulk_import(
        assessment_subject_id=asub.id,
        grades=[{"enrollment_id": e1.id, "raw_score": Decimal("-1.0")}],
    )
    assert preview2["errors"] and preview2["errors"][0]["code"] == "negative_score"

    # Present but raw_score missing
    preview3 = StudentAssessmentService.preview_bulk_import(
        assessment_subject_id=asub.id,
        grades=[{"enrollment_id": e1.id}],
    )
    assert preview3["errors"] and preview3["errors"][0]["code"] == "score_required_when_present"
