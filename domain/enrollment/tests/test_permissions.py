"""Tests for portal-based permissions."""

import pytest
from django.test import RequestFactory

from domain.account.models import CustomUser
from domain.enrollment.api.permissions import (
    HasPortalRole,
    IsParent,
    IsSchoolStaffOrAdmin,
    IsStudent,
    IsTeacher,
)
from domain.enrollment.api.views.roster import MyEnrollmentsView


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def user(db):
    return CustomUser.objects.create_user(
        email="test@example.com",
        password="pass",
        first_name="Test",
        last_name="User",
    )


@pytest.mark.django_db
def test_is_school_staff_or_admin_permission(rf, user):
    request = rf.get("/")
    request.user = user
    request.session = {"current_role": "SCHOOL_ADMIN"}

    permission = IsSchoolStaffOrAdmin()
    view = MyEnrollmentsView()

    assert permission.has_permission(request, view) is True


@pytest.mark.django_db
def test_is_student_permission(rf, user):
    request = rf.get("/")
    request.user = user
    request.session = {"current_role": "STUDENT"}

    permission = IsStudent()
    view = MyEnrollmentsView()

    assert permission.has_permission(request, view) is True


@pytest.mark.django_db
def test_is_student_permission_denied_for_staff(rf, user):
    request = rf.get("/")
    request.user = user
    request.session = {"current_role": "STAFF"}

    permission = IsStudent()
    view = MyEnrollmentsView()

    assert permission.has_permission(request, view) is False


@pytest.mark.django_db
def test_has_portal_role_without_session_role(rf, user):
    request = rf.get("/")
    request.user = user
    request.session = {}

    permission = HasPortalRole()
    view = MyEnrollmentsView()

    assert permission.has_permission(request, view) is False
