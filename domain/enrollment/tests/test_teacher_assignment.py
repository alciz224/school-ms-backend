"""Tests for TeacherAssignment business logic."""

import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from domain.account.models import CustomUser
from domain.academic.models import Subject
from domain.enrollment.constants import TeacherAssignmentStatus
from domain.enrollment.services import TeacherAssignmentService
from domain.school_operations.constants import SchoolYearTeacherStatus
from domain.school_operations.models import SchoolYearLevelSubject, SchoolYearTeacher
from domain.shared.exceptions import BusinessRuleException


@pytest.mark.django_db
def test_create_teacher_assignment_success(school_year_level, classroom_a, school_year):
    # Create a teacher and assign to school year
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com", password="pass", first_name="John", last_name="Doe"
    )
    school_year_teacher = SchoolYearTeacher.objects.create(
        school_year=school_year,
        teacher=teacher,
        status=SchoolYearTeacherStatus.ACTIVE,
    )
    
    # Create subject for the level
    subject = Subject.objects.create(name="Math", code="MATH")
    school_year_level_subject = SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level,
        subject=subject,
        coefficient=Decimal("2.0"),
    )

    # Create assignment
    assignment = TeacherAssignmentService.create(
        school_year_teacher=school_year_teacher,
        classroom=classroom_a,
        school_year_level_subject=school_year_level_subject,
        start_date=datetime.date(2025, 9, 1),
    )

    assert assignment.assignment_status == TeacherAssignmentStatus.ACTIVE
    assert assignment.school_year_teacher == school_year_teacher
    assert assignment.classroom == classroom_a
    assert assignment.is_active is True


@pytest.mark.django_db
def test_cannot_create_duplicate_active_assignment(school_year_level, classroom_a, school_year):
    teacher1 = CustomUser.objects.create_user(
        email="teacher1@example.com", password="pass", first_name="John", last_name="Doe"
    )
    teacher2 = CustomUser.objects.create_user(
        email="teacher2@example.com", password="pass", first_name="Jane", last_name="Smith"
    )
    
    school_year_teacher1 = SchoolYearTeacher.objects.create(
        school_year=school_year, teacher=teacher1, status=SchoolYearTeacherStatus.ACTIVE
    )
    school_year_teacher2 = SchoolYearTeacher.objects.create(
        school_year=school_year, teacher=teacher2, status=SchoolYearTeacherStatus.ACTIVE
    )

    subject = Subject.objects.create(name="Math", code="MATH")
    school_year_level_subject = SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level, subject=subject, coefficient=Decimal("2.0")
    )

    # First assignment succeeds
    TeacherAssignmentService.create(
        school_year_teacher=school_year_teacher1,
        classroom=classroom_a,
        school_year_level_subject=school_year_level_subject,
        start_date=datetime.date(2025, 9, 1),
    )

    # Second assignment for same classroom+subject should fail
    with pytest.raises(BusinessRuleException) as exc_info:
        TeacherAssignmentService.create(
            school_year_teacher=school_year_teacher2,
            classroom=classroom_a,
            school_year_level_subject=school_year_level_subject,
            start_date=datetime.date(2025, 9, 1),
        )
    
    assert exc_info.value.rule == "assignment_already_exists"


@pytest.mark.django_db
def test_cannot_create_assignment_for_inactive_teacher(school_year_level, classroom_a, school_year):
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com", password="pass", first_name="John", last_name="Doe"
    )
    school_year_teacher = SchoolYearTeacher.objects.create(
        school_year=school_year,
        teacher=teacher,
        status=SchoolYearTeacherStatus.SUSPENDED,  # Not ACTIVE
    )

    subject = Subject.objects.create(name="Math", code="MATH")
    school_year_level_subject = SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level, subject=subject, coefficient=Decimal("2.0")
    )

    with pytest.raises(BusinessRuleException) as exc_info:
        TeacherAssignmentService.create(
            school_year_teacher=school_year_teacher,
            classroom=classroom_a,
            school_year_level_subject=school_year_level_subject,
            start_date=datetime.date(2025, 9, 1),
        )
    
    assert exc_info.value.rule == "teacher_not_active"


@pytest.mark.django_db
def test_end_assignment(school_year_level, classroom_a, school_year):
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com", password="pass", first_name="John", last_name="Doe"
    )
    school_year_teacher = SchoolYearTeacher.objects.create(
        school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE
    )

    subject = Subject.objects.create(name="Math", code="MATH")
    school_year_level_subject = SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level, subject=subject, coefficient=Decimal("2.0")
    )

    assignment = TeacherAssignmentService.create(
        school_year_teacher=school_year_teacher,
        classroom=classroom_a,
        school_year_level_subject=school_year_level_subject,
        start_date=datetime.date(2025, 9, 1),
    )

    # End the assignment
    ended = TeacherAssignmentService.end(
        obj=assignment, end_date=datetime.date(2025, 12, 1)
    )

    assert ended.assignment_status == TeacherAssignmentStatus.ENDED
    assert ended.end_date == datetime.date(2025, 12, 1)
    assert ended.is_active is False


@pytest.mark.django_db
def test_replace_teacher(school_year_level, classroom_a, school_year):
    # Original teacher
    teacher1 = CustomUser.objects.create_user(
        email="teacher1@example.com", password="pass", first_name="John", last_name="Doe"
    )
    school_year_teacher1 = SchoolYearTeacher.objects.create(
        school_year=school_year, teacher=teacher1, status=SchoolYearTeacherStatus.ACTIVE
    )
    
    # Replacement teacher
    teacher2 = CustomUser.objects.create_user(
        email="teacher2@example.com", password="pass", first_name="Jane", last_name="Smith"
    )
    school_year_teacher2 = SchoolYearTeacher.objects.create(
        school_year=school_year, teacher=teacher2, status=SchoolYearTeacherStatus.ACTIVE
    )

    subject = Subject.objects.create(name="Math", code="MATH")
    school_year_level_subject = SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level, subject=subject, coefficient=Decimal("2.0")
    )

    # Original assignment
    assignment = TeacherAssignmentService.create(
        school_year_teacher=school_year_teacher1,
        classroom=classroom_a,
        school_year_level_subject=school_year_level_subject,
        start_date=datetime.date(2025, 9, 1),
    )

    # Replace
    new_assignment = TeacherAssignmentService.replace(
        obj=assignment,
        new_school_year_teacher=school_year_teacher2,
        start_date=datetime.date(2025, 11, 1),
    )

    # Check old assignment
    assignment.refresh_from_db()
    assert assignment.assignment_status == TeacherAssignmentStatus.REPLACED
    assert assignment.end_date == datetime.date(2025, 11, 1)
    assert assignment.replaced_by == new_assignment

    # Check new assignment
    assert new_assignment.assignment_status == TeacherAssignmentStatus.ACTIVE
    assert new_assignment.start_date == datetime.date(2025, 11, 1)
    assert new_assignment.school_year_teacher == school_year_teacher2
    assert new_assignment.classroom == classroom_a
    assert new_assignment.school_year_level_subject == school_year_level_subject


@pytest.mark.django_db
def test_assignment_model_validation_coherence(school_year_level, classroom_a, school_year):
    """Test model validation for classroom/subject/school_year coherence."""
    
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com", password="pass", first_name="John", last_name="Doe"
    )
    school_year_teacher = SchoolYearTeacher.objects.create(
        school_year=school_year, teacher=teacher, status=SchoolYearTeacherStatus.ACTIVE
    )

    # Create subject for a DIFFERENT school year level (should fail)
    other_cycle = school_year_level.school_year_cycle
    from domain.academic.models import Level
    other_level = Level.objects.create(name="2nd", code="L2", order=2, cycle=other_cycle.cycle)
    from domain.school_operations.models import SchoolYearLevel
    other_school_year_level = SchoolYearLevel.objects.create(
        school_year_cycle=other_cycle,
        level=other_level,
    )

    subject = Subject.objects.create(name="Math", code="MATH")
    other_school_year_level_subject = SchoolYearLevelSubject.objects.create(
        school_year_level=other_school_year_level, subject=subject, coefficient=Decimal("2.0")
    )

    from domain.enrollment.models import TeacherAssignment
    # This should fail validation
    assignment = TeacherAssignment(
        school_year_teacher=school_year_teacher,
        classroom=classroom_a,  # belongs to school_year_level
        school_year_level_subject=other_school_year_level_subject,  # belongs to other_school_year_level
        start_date=datetime.date(2025, 9, 1),
    )

    with pytest.raises(ValidationError) as exc_info:
        assignment.full_clean()
    
    assert "Subject must belong to the same SchoolYearLevel" in str(exc_info.value)