"""Smoke test that our URL patterns match API_ENDPOINTS.md.

This doesn't validate full behavior, only that endpoints are wired.
"""

import pytest
from django.urls import resolve


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/auth/login/",
        "/api/v1/auth/register/",
        "/api/v1/auth/logout/",
        "/api/v1/auth/refresh/",
        "/api/v1/auth/me/",
        "/api/v1/auth/me/email/",
        "/api/v1/auth/me/phone/",
        "/api/v1/auth/verify/status/",
        "/api/v1/auth/verify/send/",
        "/api/v1/auth/verify/confirm/",
        "/api/v1/auth/password/change/",
        "/api/v1/auth/password/reset/",
        "/api/v1/auth/password/reset/confirm/",
        "/api/v1/auth/password/strength/",
        "/api/v1/auth/security-questions/",
        "/api/v1/auth/security-questions/mine/",
        "/api/v1/auth/security-questions/setup/",
        "/api/v1/auth/security-questions/verify/",
    ],
)
def test_url_resolves(path):
    """Test that all API contract URLs resolve to a view."""
    match = resolve(path)
    assert match is not None
