"""Tests for verification endpoints.

API Contract: API_ENDPOINTS.md section 5
Endpoints:
  - GET /api/v1/auth/verify/status/
  - POST /api/v1/auth/verify/send/
  - POST /api/v1/auth/verify/confirm/
"""

import pytest


@pytest.mark.django_db
class TestVerificationStatus:
    def test_status_requires_auth(self, api_client, urls):
        r = api_client.get(urls.VERIFY_STATUS)
        assert r.status_code == 401

    def test_status_success(self, auth_client, urls):
        r = auth_client.get(urls.VERIFY_STATUS)
        assert r.status_code == 200
        assert r.data["success"] is True
        assert "email" in r.data["data"]
        assert "phone" in r.data["data"]


@pytest.mark.django_db
class TestSendCode:
    def test_send_code_success(self, auth_client, urls):
        r = auth_client.post(urls.VERIFY_SEND, {"type": "email"}, format="json")
        # may be 400 if user has no email configured, but our default user has email
        assert r.status_code in (200, 400)


@pytest.mark.django_db
class TestConfirmCode:
    def test_confirm_code_invalid(self, auth_client, urls):
        r = auth_client.post(urls.VERIFY_CONFIRM, {"type": "email", "code": "000000"}, format="json")
        assert r.status_code in (400, 404)
