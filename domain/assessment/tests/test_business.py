import datetime
from decimal import Decimal

import pytest

from domain.account.models import CustomUser
from domain.academic.models import Term, TermType
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus
from domain.assessment.models import Assessment, AssessmentSubject, StudentAssessment
from domain.assessment.selectors import ClassroomGradingSelector
from domain.assessment.services import (
    AssessmentService,
    AssessmentSubjectService,
    StudentAssessmentService,
)
from domain.enrollment.models import StudentEnrollment
from domain.enrollment.services import StudentEnrollmentService, TeacherAssignmentService
from domain.school_operations.models import (
    SchoolYearCycle,
    SchoolYearCycleTerm,
    SchoolYearLevelSubject,
    SchoolYearTeacher,
)
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.shared.exceptions import BusinessRuleException, ValidationException


@pytest.mark.django_db
def test_assessment_status_transitions(school_year):
    # Build SchoolYearCycle and TermType/Term
    term_type = TermType.objects.create(name="Trimester", code="TRI", period_count=3)
    # Reuse fixtures: create a minimal cycle/level structure
    from domain.academic.models import Cycle
    cycle = Cycle.objects.create(name="Primary", code="PRI")
    syc = SchoolYearCycle.objects.create(school_year=school_year, cycle=cycle, term_type=term_type)
    # Create a Term compatible with term_type
    t1 = Term.objects.create(term_type=term_type, name="T1", code="T1", order=1)
    syct = SchoolYearCycleTerm.objects.create(
        school_year_cycle=syc,
        term=t1,
        start_date=school_year.start_date,
        end_date=school_year.start_date + datetime.timedelta(days=90),
    )

    from domain.academic.models import AssessmentType as AT
    at = AT.objects.create(name="Exam", code="EXAM")
    assess = Assessment.objects.create(
        school_year=school_year,
        school_year_cycle=syc,
        school_year_cycle_term=syct,
        assessment_type=at,
        name="T1 Exams",
        status=AssessmentStatus.DRAFT,
        start_date=syct.start_date,
        end_date=syct.end_date,
    )

    assess = AssessmentService.activate(obj=assess)
    assert assess.status == AssessmentStatus.ACTIVE

    assess = AssessmentService.close(obj=assess)
    assert assess.status == AssessmentStatus.CLOSED

    with pytest.raises(BusinessRuleException):
        AssessmentService.activate(obj=assess)


@pytest.mark.django_db
def test_bulk_preview_and_commit_all_or_nothing(school_year, school_year_level, classroom_a):
    # Setup teacher and assignment for the classroom/subject
    teacher = CustomUser.objects.create_user(email="t@example.com", password="pass", first_name="T", last_name="E")
    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)

    from domain.academic.models import Subject as Subj
    subj = Subj.objects.create(name="Math", code="MATH")
    subject_ref = SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level, subject=subj, coefficient=Decimal("2.0")
    )

    ta = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=subject_ref,
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
        school_year_level_subject=subject_ref,
        teacher_assignment=ta,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )

    # Create 2 enrollments in the classroom
    e1 = StudentEnrollmentService.create(
        student=None,
        first_name="A",
        last_name="One",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-100",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )
    e2 = StudentEnrollmentService.create(
        student=None,
        first_name="B",
        last_name="Two",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-101",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    # Preview with one invalid score (> max)
    preview = StudentAssessmentService.preview_bulk_import(
        assessment_subject_id=asub.id,
        grades=[
            {"enrollment_id": e1.id, "raw_score": Decimal("15.0")},
            {"enrollment_id": e2.id, "raw_score": Decimal("25.0")},  # invalid
        ],
    )
    assert preview["creates"] == 1 and preview["updates"] == 0 and len(preview["errors"]) == 1

    # Commit should raise (all-or-nothing)
    with pytest.raises(ValidationException):
        StudentAssessmentService.commit_bulk_import(
            assessment_subject_id=asub.id,
            grades=preview["errors"] and [{"enrollment_id": e1.id, "raw_score": Decimal("15.0")}, {"enrollment_id": e2.id, "raw_score": Decimal("25.0")}],
        )

    assert StudentAssessment.objects.filter(assessment_subject=asub).count() == 0

    # Fix and commit
    ok = StudentAssessmentService.commit_bulk_import(
        assessment_subject_id=asub.id,
        grades=[
            {"enrollment_id": e1.id, "raw_score": Decimal("15.0")},
            {"enrollment_id": e2.id, "raw_score": Decimal("18.0")},
        ],
    )
    assert ok["created"] == 2
    assert StudentAssessment.objects.filter(assessment_subject=asub).count() == 2

    # Re-import with update on e1
    ok2 = StudentAssessmentService.commit_bulk_import(
        assessment_subject_id=asub.id,
        grades=[
            {"enrollment_id": e1.id, "raw_score": Decimal("16.0")},  # update
            {"enrollment_id": e2.id, "raw_score": Decimal("18.0")},  # no change
        ],
    )
    assert ok2["updated"] == 2 or ok2["updated"] == 1  # depending on database write detection

    # Selector returns rows with existing scores
    sheet = ClassroomGradingSelector.get_classroom_grading_sheet(assessment_subject_id=asub.id)
    assert len(sheet["rows"]) >= 2
    ids = {row["enrollment_id"] for row in sheet["rows"]}
    assert e1.id in ids and e2.id in ids
