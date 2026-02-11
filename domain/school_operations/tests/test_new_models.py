"""Tests for newly added school_operations models."""

import datetime
from decimal import Decimal

import pytest
from django.core.exceptions import ValidationError

from domain.academic.models import Subject, Term, TermType
from domain.account.models import CustomUser
from domain.school_operations.models import (
    SchoolYearCycleTerm,
    SchoolYearCycleTimeSlot,
    SchoolYearLevelSubject,
    SchoolYearTeacher,
)


@pytest.mark.django_db
def test_school_year_level_subject_unique(school_year_level):
    subject = Subject.objects.create(name="Math", code="MATH")
    SchoolYearLevelSubject.objects.create(
        school_year_level=school_year_level, subject=subject, coefficient=Decimal("2.0")
    )

    with pytest.raises(ValidationError):
        SchoolYearLevelSubject.objects.create(
            school_year_level=school_year_level, subject=subject, coefficient=Decimal("1.5")
        )


@pytest.mark.django_db
def test_school_year_cycle_term_dates_coherence(school_year_cycle):
    term_type = school_year_cycle.term_type
    term = Term.objects.create(term_type=term_type, name="T1", code="T1", order=1)

    term_obj = SchoolYearCycleTerm(
        school_year_cycle=school_year_cycle,
        term=term,
        start_date=datetime.date(2025, 12, 1),
        end_date=datetime.date(2025, 10, 1),  # end before start
    )

    with pytest.raises(ValidationError):
        term_obj.full_clean()


@pytest.mark.django_db
def test_school_year_teacher_unique(school_year):
    teacher = CustomUser.objects.create_user(
        email="teacher@example.com", password="pass", first_name="Test", last_name="Teacher"
    )
    SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status="ACTIVE")

    with pytest.raises(ValidationError):
        SchoolYearTeacher.objects.create(school_year=school_year, teacher=teacher, status="ACTIVE")


@pytest.mark.django_db
def test_school_year_cycle_time_slot_times_valid(school_year_cycle):
    slot = SchoolYearCycleTimeSlot(
        school_year_cycle=school_year_cycle,
        name="Slot 1",
        start_time=datetime.time(10, 0),
        end_time=datetime.time(9, 0),  # end before start
        order=1,
    )

    with pytest.raises(ValidationError):
        slot.full_clean()
