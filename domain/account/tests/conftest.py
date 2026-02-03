"""
Pytest fixtures for account tests.

Provides common fixtures for user creation, authentication, and API client setup.
"""

import pytest


@pytest.fixture
def api_client():
    """Return an unauthenticated API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def user_data():
    """Return valid user registration data."""
    return {
        "email": "testuser@example.com",
        "phone": "+224620123456",
        "password": "TestPass123!",
        "password_confirm": "TestPass123!",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def user(db):
    """Create and return a test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email="testuser@example.com",
        phone="+224620123456",
        password="TestPass123!",
        first_name="Test",
        last_name="User",
    )


@pytest.fixture
def verified_user(db):
    """Create and return a verified test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(
        email="verified@example.com",
        phone="+224620111111",
        password="TestPass123!",
        first_name="Verified",
        last_name="User",
    )
    user.email_verified = True
    user.phone_verified = True
    user.save()
    return user


@pytest.fixture
def another_user(db):
    """Create and return another test user."""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    return User.objects.create_user(
        email="another@example.com",
        phone="+224620999999",
        password="AnotherPass123!",
        first_name="Another",
        last_name="User",
    )


@pytest.fixture
def auth_client(api_client, user):
    """Return an authenticated API client."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def verified_auth_client(api_client, verified_user):
    """Return an authenticated API client for verified user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(verified_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}")
    return api_client


@pytest.fixture
def tokens(user):
    """Return access and refresh tokens for a user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


# URL helpers
class URLs:
    """API endpoint URLs."""
    
    # Auth
    LOGIN = "/api/v1/auth/login/"
    REGISTER = "/api/v1/auth/register/"
    LOGOUT = "/api/v1/auth/logout/"
    REFRESH = "/api/v1/auth/refresh/"
    
    # User Profile
    ME = "/api/v1/auth/me/"
    ME_EMAIL = "/api/v1/auth/me/email/"
    ME_PHONE = "/api/v1/auth/me/phone/"
    
    # Verification
    VERIFY_STATUS = "/api/v1/auth/verify/status/"
    VERIFY_SEND = "/api/v1/auth/verify/send/"
    VERIFY_CONFIRM = "/api/v1/auth/verify/confirm/"
    
    # Password
    PASSWORD_CHANGE = "/api/v1/auth/password/change/"
    PASSWORD_RESET = "/api/v1/auth/password/reset/"
    PASSWORD_RESET_CONFIRM = "/api/v1/auth/password/reset/confirm/"
    PASSWORD_STRENGTH = "/api/v1/auth/password/strength/"
    
    # Security Questions
    SECURITY_QUESTIONS = "/api/v1/auth/security-questions/"
    SECURITY_QUESTIONS_MINE = "/api/v1/auth/security-questions/mine/"
    SECURITY_QUESTIONS_SETUP = "/api/v1/auth/security-questions/setup/"
    SECURITY_QUESTIONS_VERIFY = "/api/v1/auth/security-questions/verify/"


@pytest.fixture
def urls():
    """Return URL helper class."""
    return URLs
