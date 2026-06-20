"""
Tests for role selection API.
"""

import pytest
from django.urls import reverse
from rest_framework import status

from domain.account.constants import UserRole, ACTIVE_ROLE_SESSION_KEY
from domain.account.models import CustomUser, ParentChild
from domain.enrollment.models import StudentEnrollment
from domain.school_operations.models import SchoolYearTeacher


@pytest.mark.django_db
class TestRoleSelection:
    """Test role selection functionality."""

    def test_select_role_requires_authentication(self, api_client):
        """Test that role selection requires authentication."""
        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.STUDENT})

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_select_valid_student_role(self, api_client, user_with_student_enrollment):
        """Test selecting student role when user has enrollment."""
        user, enrollment = user_with_student_enrollment
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.STUDENT})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["role"] == UserRole.STUDENT
        assert response.data["message"] == "Role selected successfully."

    def test_select_invalid_role_returns_403(self, api_client, user):
        """Test selecting a role that user doesn't have access to."""
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.STUDENT})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_select_role_stores_in_session(self, api_client, user_with_student_enrollment):
        """Test that selected role is stored in session."""
        user, enrollment = user_with_student_enrollment
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")
        api_client.post(url, {"role": UserRole.STUDENT})

        # Check session
        session = api_client.session
        assert session[ACTIVE_ROLE_SESSION_KEY] == UserRole.STUDENT

    def test_switch_between_roles(self, api_client, user_with_multiple_roles):
        """Test switching between different roles."""
        user = user_with_multiple_roles
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")

        # Select student role
        response = api_client.post(url, {"role": UserRole.STUDENT})
        assert response.status_code == status.HTTP_200_OK
        assert api_client.session[ACTIVE_ROLE_SESSION_KEY] == UserRole.STUDENT

        # Switch to teacher role
        response = api_client.post(url, {"role": UserRole.TEACHER})
        assert response.status_code == status.HTTP_200_OK
        assert api_client.session[ACTIVE_ROLE_SESSION_KEY] == UserRole.TEACHER

    def test_select_teacher_role(self, api_client, user_with_teacher_assignment):
        """Test selecting teacher role when user has teaching assignments."""
        user, teacher_assignment = user_with_teacher_assignment
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.TEACHER})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == UserRole.TEACHER

    def test_select_parent_role(self, api_client, user_with_parent_relationship):
        """Test selecting parent role when user has parent relationships."""
        user, parent_child = user_with_parent_relationship
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.PARENT})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == UserRole.PARENT

    def test_select_admin_role(self, api_client, staff_user):
        """Test selecting admin role when user is staff."""
        api_client.force_authenticate(user=staff_user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.ADMIN})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == UserRole.ADMIN

    def test_select_school_admin_role(self, api_client, staff_user):
        """Test selecting school_admin role when user is staff."""
        api_client.force_authenticate(user=staff_user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.SCHOOL_ADMIN})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == UserRole.SCHOOL_ADMIN

    def test_select_super_admin_role(self, api_client, superuser):
        """Test selecting super_admin role when user is superuser."""
        api_client.force_authenticate(user=superuser)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": UserRole.SUPER_ADMIN})

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["role"] == UserRole.SUPER_ADMIN

    def test_invalid_role_format(self, api_client, user):
        """Test providing invalid role format."""
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {"role": "invalid_role"})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False

    def test_missing_role_field(self, api_client, user):
        """Test missing role field in request."""
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:select_role")
        response = api_client.post(url, {})

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False


@pytest.mark.django_db
class TestUserSerializerWithRoles:
    """Test UserSerializer includes role information."""

    def test_user_serializer_includes_available_roles(self, api_client, user_with_student_enrollment):
        """Test that UserSerializer includes available_roles field."""
        user, enrollment = user_with_student_enrollment
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:status")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert "available_roles" in response.data["data"]["user"]
        assert UserRole.STUDENT in response.data["data"]["user"]["available_roles"]

    def test_user_serializer_includes_active_role(self, api_client, user_with_student_enrollment):
        """Test that UserSerializer includes active_role field."""
        user, enrollment = user_with_student_enrollment
        api_client.force_authenticate(user=user)

        # Select a role first
        select_url = reverse("account_v2:select_role")
        api_client.post(select_url, {"role": UserRole.STUDENT})

        # Check status
        status_url = reverse("account_v2:status")
        response = api_client.get(status_url)

        assert response.status_code == status.HTTP_200_OK
        assert "active_role" in response.data["data"]["user"]
        assert response.data["data"]["user"]["active_role"] == UserRole.STUDENT

    def test_active_role_is_null_when_not_set(self, api_client, user):
        """Test that active_role is None when not set in session."""
        api_client.force_authenticate(user=user)

        url = reverse("account_v2:status")
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["user"]["active_role"] is None


@pytest.mark.django_db
class TestDefaultRoleOnLogin:
    """Test that default role is set on login."""

    def test_default_role_set_on_login(self, api_client, user_with_student_enrollment):
        """Test that default role is automatically set on login."""
        user, enrollment = user_with_student_enrollment
        user.set_password("testpass123")
        user.save()

        url = reverse("account_v2:login")
        response = api_client.post(url, {
            "identifier": user.email,
            "password": "testpass123"
        })

        assert response.status_code == status.HTTP_200_OK
        assert "available_roles" in response.data["data"]["user"]
        assert "active_role" in response.data["data"]["user"]
        # Student role should be set as default (highest priority)
        assert response.data["data"]["user"]["active_role"] == UserRole.STUDENT

    def test_default_role_priority_student_over_teacher(self, api_client, user_with_multiple_roles):
        """Test that student role has priority over teacher when both available."""
        user = user_with_multiple_roles
        user.set_password("testpass123")
        user.save()

        url = reverse("account_v2:login")
        response = api_client.post(url, {
            "identifier": user.email,
            "password": "testpass123"
        })

        assert response.status_code == status.HTTP_200_OK
        # Student should be selected by default (higher priority)
        assert response.data["data"]["user"]["active_role"] == UserRole.STUDENT

    def test_no_default_role_for_user_without_roles(self, api_client, user):
        """Test that no role is set if user has no available roles."""
        user.set_password("testpass123")
        user.save()

        url = reverse("account_v2:login")
        response = api_client.post(url, {
            "identifier": user.email,
            "password": "testpass123"
        })

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["user"]["active_role"] is None
        assert response.data["data"]["user"]["available_roles"] == []


@pytest.mark.django_db
class TestRoleDetectionLogic:
    """Test role detection based on relationships."""

    def test_student_role_detected_with_enrollment(self, user_with_student_enrollment):
        """Test student role is detected when user has enrollment."""
        from domain.account.selectors import UserRoleSelector
        
        user, enrollment = user_with_student_enrollment
        roles = UserRoleSelector.get_available_roles(user)

        assert UserRole.STUDENT in roles

    def test_teacher_role_detected_with_assignment(self, user_with_teacher_assignment):
        """Test teacher role is detected when user has teaching assignment."""
        from domain.account.selectors import UserRoleSelector
        
        user, teacher_assignment = user_with_teacher_assignment
        roles = UserRoleSelector.get_available_roles(user)

        assert UserRole.TEACHER in roles

    def test_parent_role_detected_with_children(self, user_with_parent_relationship):
        """Test parent role is detected when user has parent relationships."""
        from domain.account.selectors import UserRoleSelector
        
        user, parent_child = user_with_parent_relationship
        roles = UserRoleSelector.get_available_roles(user)

        assert UserRole.PARENT in roles

    def test_admin_role_detected_for_staff(self, staff_user):
        """Test admin role is detected for staff users."""
        from domain.account.selectors import UserRoleSelector
        
        roles = UserRoleSelector.get_available_roles(staff_user)

        assert UserRole.ADMIN in roles
        assert UserRole.SCHOOL_ADMIN in roles

    def test_super_admin_role_detected_for_superuser(self, superuser):
        """Test super_admin role is detected for superusers."""
        from domain.account.selectors import UserRoleSelector
        
        roles = UserRoleSelector.get_available_roles(superuser)

        assert UserRole.SUPER_ADMIN in roles

    def test_no_roles_for_basic_user(self, user):
        """Test that basic user with no relationships has no roles."""
        from domain.account.selectors import UserRoleSelector
        
        roles = UserRoleSelector.get_available_roles(user)

        assert roles == []

    def test_deleted_enrollment_not_counted(self, user_with_student_enrollment):
        """Test that soft-deleted enrollments don't count for role detection."""
        from domain.account.selectors import UserRoleSelector
        
        user, enrollment = user_with_student_enrollment
        
        # Soft delete the enrollment
        enrollment.is_deleted = True
        enrollment.is_active = False
        enrollment.save()

        roles = UserRoleSelector.get_available_roles(user)

        assert UserRole.STUDENT not in roles
