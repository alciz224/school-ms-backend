"""Tests for security question endpoints.

API Contract: API_ENDPOINTS.md section 6
Endpoints:
  - GET /api/v1/auth/security-questions/
  - GET /api/v1/auth/security-questions/mine/
  - POST /api/v1/auth/security-questions/setup/
  - POST /api/v1/auth/security-questions/verify/
"""

import pytest


@pytest.mark.django_db
class TestPredefined:
    def test_get_predefined_questions(self, api_client, urls):
        r = api_client.get(urls.SECURITY_QUESTIONS)
        assert r.status_code == 200
        assert r.data["success"] is True
        assert "predefined_questions" in r.data["data"]


@pytest.mark.django_db
class TestMine:
    def test_get_mine_requires_auth(self, api_client, urls):
        r = api_client.get(urls.SECURITY_QUESTIONS_MINE)
        assert r.status_code == 401

    def test_get_mine_success(self, auth_client, urls):
        r = auth_client.get(urls.SECURITY_QUESTIONS_MINE)
        assert r.status_code == 200
        assert r.data["success"] is True
        assert "configured_count" in r.data["data"]
        assert "questions" in r.data["data"]


@pytest.mark.django_db
class TestSetup:
    def test_setup_questions_success(self, auth_client, urls):
        payload = {
            "questions": [
                {"question": "What is your favorite color?", "answer": "Blue"},
                {"question": "What is your pet's name?", "answer": "Max"},
            ]
        }
        r = auth_client.post(urls.SECURITY_QUESTIONS_SETUP, payload, format="json")
        assert r.status_code in (200, 201)
        assert r.data["success"] is True
        assert "configured_count" in r.data["data"]


@pytest.mark.django_db
class TestVerify:
    def test_verify_answers_invalid_identifier(self, api_client, urls):
        payload = {
            "identifier": "unknown@example.com",
            "answers": [{"order": 1, "answer": "A1"}, {"order": 2, "answer": "A2"}],
        }
        r = api_client.post(urls.SECURITY_QUESTIONS_VERIFY, payload, format="json")
        assert r.status_code in (400, 404)
