# domain/accounts/tests/test_api_user.py

"""
Tests API pour le profil utilisateur.
"""

import pytest
from rest_framework import status


@pytest.mark.django_db
class TestMeAPI:
    """Tests pour GET/PATCH /api/v1/auth/me/"""

    url = "/api/v1/auth/me/"

    def test_get_profile_success(self, authenticated_client, user):
        """Récupérer son profil."""
        response = authenticated_client.get(self.url)

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert response.data["data"]["email"] == user.email
        assert "verification" in response.data["data"]
        assert "security" in response.data["data"]

    def test_get_profile_unauthenticated(self, api_client):
        """Échec si non authentifié."""
        response = api_client.get(self.url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_update_profile_success(self, authenticated_client):
        """Mettre à jour son profil."""
        data = {
            "first_name": "Updated",
            "last_name": "Name",
            "backup_phone": "+224622000000",
            "backup_phone_owner": "Maman",
        }

        response = authenticated_client.patch(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["first_name"] == "Updated"
        assert response.data["data"]["backup_phone"] == "+224622000000"

    def test_update_partial(self, authenticated_client):
        """Mise à jour partielle."""
        data = {"first_name": "OnlyFirst"}

        response = authenticated_client.patch(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["first_name"] == "OnlyFirst"


@pytest.mark.django_db
class TestUpdateEmailAPI:
    """Tests pour POST /api/v1/auth/me/email/"""

    url = "/api/v1/auth/me/email/"

    def test_update_email_success(self, authenticated_client, user_data):
        """Modifier son email."""
        data = {
            "email": "newemail@example.com",
            "current_password": user_data["password"],
        }

        response = authenticated_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["email"] == "newemail@example.com"
        assert response.data["data"]["email_verified"] is False

    def test_update_email_wrong_password(self, authenticated_client):
        """Échec avec mauvais mot de passe."""
        data = {"email": "newemail@example.com", "current_password": "WrongPassword"}

        response = authenticated_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestUpdatePhoneAPI:
    """Tests pour POST /api/v1/auth/me/phone/"""

    url = "/api/v1/auth/me/phone/"

    def test_update_phone_success(self, authenticated_client, user_data):
        """Modifier son téléphone."""
        data = {"phone": "+224625000000", "current_password": user_data["password"]}

        response = authenticated_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["data"]["phone_verified"] is False

    def test_update_phone_invalid_format(self, authenticated_client, user_data):
        """Échec avec format invalide."""
        data = {"phone": "123", "current_password": user_data["password"]}

        response = authenticated_client.post(self.url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
