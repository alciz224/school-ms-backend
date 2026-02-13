import datetime
from decimal import Decimal

import pytest

from domain.account.models import CustomUser
from domain.academic.models import AssessmentType, Subject, Term
from domain.assessment.constants import AssessmentStatus, AssessmentSubjectStatus, StudentAssessmentStatus
from domain.assessment.models import Assessment, AssessmentSubject, StudentAssessment
from domain.assessment.services import ReportCardService, TranscriptService
from domain.enrollment.services import StudentEnrollmentService, TeacherAssignmentService
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import SchoolYearCycleTerm, SchoolYearLevelSubject, SchoolYearTeacher


@pytest.mark.django_db
def test_report_card_generation_weighted_average(school_year, school_year_level, classroom_a):
    # Setup teacher + assignment
    teacher = CustomUser.objects.create_user(email="t@example.com", password="pass", first_name="T", last_name="A")
    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)

    subj_math = Subject.objects.create(name="Math", code="MATH")
    subj_fr = Subject.objects.create(name="French", code="FR")
    syls_math = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subj_math, coefficient=Decimal("2.0"))
    syls_fr = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subj_fr, coefficient=Decimal("1.0"))

    ta_math = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls_math,
        start_date=school_year.start_date,
    )
    ta_fr = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls_fr,
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

    asub_math = AssessmentSubject.objects.create(
        assessment=assessment,
        classroom=classroom_a,
        school_year_level_subject=syls_math,
        teacher_assignment=ta_math,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )
    asub_fr = AssessmentSubject.objects.create(
        assessment=assessment,
        classroom=classroom_a,
        school_year_level_subject=syls_fr,
        teacher_assignment=ta_fr,
        status=AssessmentSubjectStatus.PUBLISHED,
        max_score=Decimal("20.0"),
    )

    student1 = StudentEnrollmentService.create(
        student=None,
        first_name="A",
        last_name="One",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-R1",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    # Validated scores
    StudentAssessment.objects.create(
        assessment_subject=asub_math,
        student_enrollment=student1,
        raw_score=Decimal("12.0"),
        status=StudentAssessmentStatus.VALIDATED,
    )
    StudentAssessment.objects.create(
        assessment_subject=asub_fr,
        student_enrollment=student1,
        raw_score=Decimal("16.0"),
        status=StudentAssessmentStatus.VALIDATED,
    )

    result = ReportCardService.generate_for_classroom_term(
        classroom=classroom_a,
        term=term_period,
    )
    assert result.report_cards_created == 1

    rc = student1.report_cards.get(school_year_cycle_term=term_period)
    # weighted avg = (12*2 + 16*1)/3 = 40/3 = 13.33
    assert rc.overall_average.quantize(Decimal("0.01")) == Decimal("13.33")


@pytest.mark.django_db
def test_transcript_generation_from_report_cards(school_year, school_year_level, classroom_a):
    # Setup teacher + subject
    teacher = CustomUser.objects.create_user(email="t2@example.com", password="pass", first_name="T", last_name="B")
    syt = SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE)

    subj_math = Subject.objects.create(name="Math", code="MATH")
    syls_math = SchoolYearLevelSubject.objects.create(school_year_level=school_year_level, subject=subj_math, coefficient=Decimal("2.0"))
    ta = TeacherAssignmentService.create(
        school_year_teacher=syt,
        classroom=classroom_a,
        school_year_level_subject=syls_math,
        start_date=school_year.start_date,
    )

    student1 = StudentEnrollmentService.create(
        student=None,
        first_name="B",
        last_name="Two",
        school_year_level=school_year_level,
        enrollment_date=school_year.start_date,
        annual_identifier="AY-R2",
        classroom=classroom_a,
        enrollment_status="ACTIVE",
    )

    at = AssessmentType.objects.create(name="Exam", code="EXAM")

    # Two terms with different averages
    for idx, score in [(1, Decimal("10.0")), (2, Decimal("14.0"))]:
        term = Term.objects.create(term_type=school_year_level.school_year_cycle.term_type, name=f"T{idx}", code=f"T{idx}", order=idx)
        term_period = SchoolYearCycleTerm.objects.create(
            school_year_cycle=school_year_level.school_year_cycle,
            term=term,
            start_date=school_year.start_date + datetime.timedelta(days=idx * 100),
            end_date=school_year.start_date + datetime.timedelta(days=idx * 100 + 90),
        )
        assessment = Assessment.objects.create(
            school_year=school_year,
            school_year_cycle=school_year_level.school_year_cycle,
            school_year_cycle_term=term_period,
            assessment_type=at,
            name=f"T{idx}",
            status=AssessmentStatus.ACTIVE,
            start_date=term_period.start_date,
            end_date=term_period.end_date,
        )
        asub = AssessmentSubject.objects.create(
            assessment=assessment,
            classroom=classroom_a,
            school_year_level_subject=syls_math,
            teacher_assignment=ta,
            status=AssessmentSubjectStatus.PUBLISHED,
            max_score=Decimal("20.0"),
        )
        StudentAssessment.objects.create(
            assessment_subject=asub,
            student_enrollment=student1,
            raw_score=score,
            status=StudentAssessmentStatus.VALIDATED,
        )
        ReportCardService.generate_for_classroom_term(classroom=classroom_a, term=term_period)

    tr = TranscriptService.generate_for_student(student_enrollment=student1, school_year=school_year)
    # average of term averages: (10 + 14) / 2 = 12
    assert tr.overall_average.quantize(Decimal("0.01")) == Decimal("12.00")
