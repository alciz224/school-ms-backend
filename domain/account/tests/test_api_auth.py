"""
Tests for authentication API endpoints.

API Contract: See API_ENDPOINTS.md sections 1-2
Endpoints:
    - POST /api/v1/auth/login/
    - POST /api/v1/auth/register/
    - POST /api/v1/auth/logout/
    - POST /api/v1/auth/refresh/
"""

import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestRegister:
    """Tests for POST /api/v1/auth/register/"""

    def test_register_with_email_success(self, api_client, urls):
        """Test successful registration with email."""
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "New",
            "last_name": "User",
        }
        response = api_client.post(urls.REGISTER, data, format="json")
        
        assert response.status_code == 201
        assert response.data["success"] is True
        assert "user" in response.data["data"]
        assert "tokens" in response.data["data"]
        assert response.data["data"]["user"]["email"] == "newuser@example.com"
        assert response.data["data"]["requires_verification"] is True

    def test_register_with_phone_success(self, api_client, urls):
        """Test successful registration with phone."""
        data = {
            "phone": "+224620555555",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Phone",
            "last_name": "User",
        }
        response = api_client.post(urls.REGISTER, data, format="json")
        
        assert response.status_code == 201
        assert response.data["success"] is True
        assert response.data["data"]["user"]["phone"] == "+224620555555"

    def test_register_with_both_email_and_phone(self, api_client, urls):
        """Test registration with both email and phone."""
        data = {
            "email": "both@example.com",
            "phone": "+224620666666",
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Both",
            "last_name": "User",
        }
        response = api_client.post(urls.REGISTER, data, format="json")
        
        assert response.status_code == 201
        assert response.data["data"]["user"]["email"] == "both@example.com"
        assert response.data["data"]["user"]["phone"] == "+224620666666"

    def test_register_password_mismatch(self, api_client, urls):
        """Test registration fails when passwords don't match."""
        data = {
            "email": "mismatch@example.com",
            "password": "SecurePass123!",
            "password_confirm": "DifferentPass123!",
            "first_name": "Test",
            "last_name": "User",
        }
        response = api_client.post(urls.REGISTER, data, format="json")
        
        assert response.status_code == 400
        assert response.data["success"] is False

    def test_register_duplicate_email(self, api_client, urls, user):
        """Test registration fails with duplicate email."""
        data = {
            "email": user.email,
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "Duplicate",
            "last_name": "User",
        }
        response = api_client.post(urls.REGISTER, data, format="json")
        
        assert response.status_code == 400
        assert response.data["success"] is False

    def test_register_weak_password(self, api_client, urls):
        """Test registration fails with weak password."""
        data = {
            "email": "weak@example.com",
            "password": "123",
            "password_confirm": "123",
            "first_name": "Weak",
            "last_name": "User",
        }
        response = api_client.post(urls.REGISTER, data, format="json")
        
        assert response.status_code == 400
        assert response.data["success"] is False

    def test_register_no_email_or_phone(self, api_client, urls):
        """Test registration fails without email or phone."""
        data = {
            "password": "SecurePass123!",
            "password_confirm": "SecurePass123!",
            "first_name": "No",
            "last_name": "Contact",
        }
        response = api_client.post(urls.REGISTER, data, format="json")
        
        assert response.status_code == 400
        assert response.data["success"] is False


@pytest.mark.django_db
class TestLogin:
    """Tests for POST /api/v1/auth/login/"""

    def test_login_with_email_success(self, api_client, urls, user):
        """Test successful login with email."""
        data = {
            "identifier": user.email,
            "password": "TestPass123!",
        }
        response = api_client.post(urls.LOGIN, data, format="json")
        
        assert response.status_code == 200
        assert response.data["success"] is True
        assert "user" in response.data["data"]
        assert "tokens" in response.data["data"]
        assert "access" in response.data["data"]["tokens"]
        assert "refresh" in response.data["data"]["tokens"]

    def test_login_with_phone_success(self, api_client, urls, user):
        """Test successful login with phone."""
        data = {
            "identifier": user.phone,
            "password": "TestPass123!",
        }
        response = api_client.post(urls.LOGIN, data, format="json")
        
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_login_invalid_credentials(self, api_client, urls, user):
        """Test login fails with wrong password."""
        data = {
            "identifier": user.email,
            "password": "WrongPassword123!",
        }
        response = api_client.post(urls.LOGIN, data, format="json")
        
        assert response.status_code == 401
        assert response.data["success"] is False

    def test_login_nonexistent_user(self, api_client, urls):
        """Test login fails for non-existent user."""
        data = {
            "identifier": "nonexistent@example.com",
            "password": "SomePassword123!",
        }
        response = api_client.post(urls.LOGIN, data, format="json")
        
        assert response.status_code == 401
        assert response.data["success"] is False

    def test_login_response_includes_security(self, api_client, urls, verified_user):
        """Test login response includes security info."""
        data = {
            "identifier": verified_user.email,
            "password": "TestPass123!",
        }
        response = api_client.post(urls.LOGIN, data, format="json")
        
        assert response.status_code == 200
        assert "security" in response.data["data"]["user"]
        assert "score" in response.data["data"]["user"]["security"]
        assert "level" in response.data["data"]["user"]["security"]


@pytest.mark.django_db
class TestLogout:
    """Tests for POST /api/v1/auth/logout/"""

    def test_logout_success(self, auth_client, urls, tokens):
        """Test successful logout."""
        data = {"refresh": tokens["refresh"]}
        response = auth_client.post(urls.LOGOUT, data, format="json")
        
        assert response.status_code == 200
        assert response.data["success"] is True

    def test_logout_unauthenticated(self, api_client, urls, tokens):
        """Test logout fails without authentication."""
        data = {"refresh": tokens["refresh"]}
        response = api_client.post(urls.LOGOUT, data, format="json")
        
        assert response.status_code == 401


@pytest.mark.django_db
class TestTokenRefresh:
    """Tests for POST /api/v1/auth/refresh/"""

    def test_refresh_token_success(self, api_client, urls, tokens):
        """Test successful token refresh."""
        data = {"refresh": tokens["refresh"]}
        response = api_client.post(urls.REFRESH, data, format="json")
        
        assert response.status_code == 200
        assert response.data["success"] is True
        assert "access" in response.data["data"]
        assert "refresh" in response.data["data"]

    def test_refresh_invalid_token(self, api_client, urls):
        """Test refresh fails with invalid token."""
        data = {"refresh": "invalid-token"}
        response = api_client.post(urls.REFRESH, data, format="json")
        
        assert response.status_code == 401
        assert response.data["success"] is False
