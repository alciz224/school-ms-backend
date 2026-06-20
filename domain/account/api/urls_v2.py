"""
URL configuration for account API v2 (session-based authentication).

All URLs are prefixed with /api/v2/auth/ in config/urls.py
API Contract: Session-based authentication for Next.js frontend.
"""

from django.urls import path

from .views.auth_v2 import (
    SessionRegisterView,
    SessionLoginView,
    SessionLogoutView,
    SessionStatusView,
    CSRFTokenView,
    SelectRoleView,
)

app_name = "account_v2"

urlpatterns = [
    # ==========================================================================
    # AUTH V2 - Session-based - /api/v2/auth/
    # ==========================================================================
    path("register/", SessionRegisterView.as_view(), name="register"),
    path("login/", SessionLoginView.as_view(), name="login"),
    path("logout/", SessionLogoutView.as_view(), name="logout"),
    path("status/", SessionStatusView.as_view(), name="status"),
    path("csrf/", CSRFTokenView.as_view(), name="csrf"),
    path("select-role/", SelectRoleView.as_view(), name="select_role"),
]
