# domain/accounts/tests/test_api_auth.py

"""
Tests API pour l'authentification.
"""

import pytest
from django.urls import reverse
from rest_framework import status


@pytest.mark.django_db
class TestRegisterAPI:
    """Tests pour POST /api/v1/auth/register/"""

    url = "/api/v1/auth/register/"

    def test_register_with_email_success(self, api_client):
        """Inscription réussie avec email."""
        data = {
            "email": "newuser@example.com",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
            "first_name": "New",
            "last_name": "User",
        }

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["success"] is True
        assert "user" in response.data["data"]
        assert "tokens" in response.data["data"]
        assert response.data["data"]["requires_verification"] is True

    def test_register_with_phone_success(self, api_client):
        """Inscription réussie avec téléphone."""
        data = {
            "phone": "+224620000010",
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
            "first_name": "Phone",
            "last_name": "User",
        }

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED

    def test_register_password_mismatch(self, api_client):
        """Échec si mots de passe différents."""
        data = {
            "email": "test@example.com",
            "password": "SecurePass123",
            "password_confirm": "DifferentPass",
            "first_name": "Test",
            "last_name": "User",
        }

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self, api_client):
        """Échec si mot de passe faible."""
        data = {
            "email": "test@example.com",
            "password": "123",
            "password_confirm": "123",
            "first_name": "Test",
            "last_name": "User",
        }

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self, api_client, user):
        """Échec si email déjà utilisé."""
        data = {
            "email": user.email,
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
            "first_name": "Dup",
            "last_name": "User",
        }

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_no_identifier(self, api_client):
        """Échec si ni email ni téléphone."""
        data = {
            "password": "SecurePass123",
            "password_confirm": "SecurePass123",
            "first_name": "No",
            "last_name": "Identifier",
        }

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:
    """Tests pour POST /api/v1/auth/login/"""

    url = "/api/v1/auth/login/"

    def test_login_with_email_success(self, api_client, user, user_data):
        """Connexion réussie avec email."""
        data = {"identifier": user.email, "password": user_data["password"]}

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "tokens" in response.data["data"]

    def test_login_with_phone_success(self, api_client, user, user_data):
        """Connexion réussie avec téléphone."""
        data = {"identifier": user.phone, "password": user_data["password"]}

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_login_invalid_password(self, api_client, user):
        """Échec avec mauvais mot de passe."""
        data = {"identifier": user.email, "password": "WrongPassword"}

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.data["success"] is False

    def test_login_unknown_user(self, api_client):
        """Échec avec utilisateur inconnu."""
        data = {"identifier": "unknown@example.com", "password": "SomePassword"}

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestLogoutAPI:
    """Tests pour POST /api/v1/auth/logout/"""

    url = "/api/v1/auth/logout/"

    def test_logout_success(self, authenticated_client, auth_tokens):
        """Déconnexion réussie."""
        data = {"refresh": auth_tokens["refresh"]}

        response = authenticated_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK

    def test_logout_unauthenticated(self, api_client):
        """Échec si non authentifié."""
        data = {"refresh": "some_token"}

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
class TestTokenRefreshAPI:
    """Tests pour POST /api/v1/auth/token/refresh/"""

    url = "/api/v1/auth/token/refresh/"

    def test_refresh_success(self, api_client, auth_tokens):
        """Rafraîchissement réussi."""
        data = {"refresh": auth_tokens["refresh"]}

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "access" in response.data["data"]

    def test_refresh_invalid_token(self, api_client):
        """Échec avec token invalide."""
        data = {"refresh": "invalid_token"}

        response = api_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
