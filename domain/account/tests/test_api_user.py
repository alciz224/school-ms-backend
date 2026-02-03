"""Tests for user profile endpoints.

API Contract: API_ENDPOINTS.md section 3
Endpoints:
  - GET/PATCH /api/v1/auth/me/
  - POST /api/v1/auth/me/email/
  - POST /api/v1/auth/me/phone/
"""

import pytest


@pytest.mark.django_db
class TestMe:
    def test_get_me_requires_auth(self, api_client, urls):
        r = api_client.get(urls.ME)
        assert r.status_code == 401

    def test_get_me_success(self, auth_client, urls):
        r = auth_client.get(urls.ME)
        assert r.status_code == 200
        assert r.data["success"] is True
        assert "data" in r.data
        assert "id" in r.data["data"]

    def test_patch_me_success(self, auth_client, urls):
        r = auth_client.patch(urls.ME, {"first_name": "Updated"}, format="json")
        assert r.status_code == 200
        assert r.data["success"] is True
        assert r.data["data"]["first_name"] == "Updated"


@pytest.mark.django_db
class TestMeEmail:
    def test_update_email_requires_auth(self, api_client, urls):
        r = api_client.post(urls.ME_EMAIL, {"email": "x@y.com", "current_password": "x"}, format="json")
        assert r.status_code == 401

    def test_update_email_success(self, auth_client, urls):
        r = auth_client.post(
            urls.ME_EMAIL,
            {"email": "new-email@example.com", "current_password": "TestPass123!"},
            format="json",
        )
        assert r.status_code == 200
        assert r.data["success"] is True
        assert r.data["data"]["email"] == "new-email@example.com"
        assert "verification_sent" in r.data["data"]


@pytest.mark.django_db
class TestMePhone:
    def test_update_phone_success(self, auth_client, urls):
        r = auth_client.post(
            urls.ME_PHONE,
            {"phone": "+224620222222", "current_password": "TestPass123!"},
            format="json",
        )
        assert r.status_code == 200
        assert r.data["success"] is True
        assert r.data["data"]["phone"] == "+224620222222"
        assert "verification_sent" in r.data["data"]
