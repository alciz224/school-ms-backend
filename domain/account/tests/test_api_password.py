"""Tests for password management endpoints.

API Contract: API_ENDPOINTS.md section 4
Endpoints:
  - POST /api/v1/auth/password/change/
  - POST /api/v1/auth/password/reset/
  - POST /api/v1/auth/password/reset/confirm/
"""

import pytest


@pytest.mark.django_db
class TestPasswordChange:
    def test_password_change_requires_auth(self, api_client, urls):
        r = api_client.post(urls.PASSWORD_CHANGE, {}, format="json")
        assert r.status_code == 401

    def test_password_change_invalid_current(self, auth_client, urls):
        payload = {
            "current_password": "WrongPass123!",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!",
        }
        r = auth_client.post(urls.PASSWORD_CHANGE, payload, format="json")
        assert r.status_code in (400, 401)


@pytest.mark.django_db
class TestPasswordReset:
    def test_password_reset_always_200(self, api_client, urls, user):
        r = api_client.post(urls.PASSWORD_RESET, {"identifier": user.email}, format="json")
        assert r.status_code == 200
        assert r.data["success"] is True
        assert "expires_in" in r.data["data"]

    def test_password_reset_unknown_identifier_also_200(self, api_client, urls):
        r = api_client.post(urls.PASSWORD_RESET, {"identifier": "unknown@example.com"}, format="json")
        assert r.status_code == 200
        assert r.data["success"] is True


@pytest.mark.django_db
class TestPasswordResetConfirm:
    def test_password_reset_confirm_invalid_code(self, api_client, urls, user):
        payload = {
            "identifier": user.email,
            "code": "000000",
            "new_password": "NewPass123!",
            "new_password_confirm": "NewPass123!",
        }
        r = api_client.post(urls.PASSWORD_RESET_CONFIRM, payload, format="json")
        assert r.status_code in (400, 404)
