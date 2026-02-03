"""
URL configuration for account API.

All URLs are prefixed with /api/auth/ in config/urls.py
API Contract: See API_ENDPOINTS.md for full specification.
"""

from django.urls import path

from .views import (
    # Auth
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshView,
    # User
    MeView,
    UpdateEmailView,
    UpdatePhoneView,
    # Verification
    SendVerificationCodeView,
    ConfirmVerificationCodeView,
    VerificationStatusView,
    # Password
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
    PasswordStrengthView,
    # Security
    UserSecurityQuestionsView,
    PredefinedQuestionsView,
    SecurityQuestionsSetupView,
    SecurityQuestionDeleteView,
    SecurityQuestionsVerifyView,
)

app_name = "account"

urlpatterns = [
    # ==========================================================================
    # AUTH - /api/auth/
    # ==========================================================================
    path("login/", LoginView.as_view(), name="login"),
    path("register/", RegisterView.as_view(), name="register"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ==========================================================================
    # USER PROFILE - /api/auth/me/
    # ==========================================================================
    path("me/", MeView.as_view(), name="me"),
    path("me/email/", UpdateEmailView.as_view(), name="update_email"),
    path("me/phone/", UpdatePhoneView.as_view(), name="update_phone"),

    # ==========================================================================
    # VERIFICATION - /api/auth/verify/
    # ==========================================================================
    path("verify/status/", VerificationStatusView.as_view(), name="verification_status"),
    path("verify/send/", SendVerificationCodeView.as_view(), name="verification_send"),
    path("verify/confirm/", ConfirmVerificationCodeView.as_view(), name="verification_confirm"),

    # ==========================================================================
    # PASSWORD - /api/auth/password/
    # ==========================================================================
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/strength/", PasswordStrengthView.as_view(), name="password_strength"),

    # ==========================================================================
    # SECURITY QUESTIONS - /api/auth/security-questions/
    # ==========================================================================
    path("security-questions/", PredefinedQuestionsView.as_view(), name="security_questions_predefined"),
    path("security-questions/mine/", UserSecurityQuestionsView.as_view(), name="security_questions_mine"),
    path("security-questions/setup/", SecurityQuestionsSetupView.as_view(), name="security_questions_setup"),
    path("security-questions/verify/", SecurityQuestionsVerifyView.as_view(), name="security_questions_verify"),
    path("security-questions/<int:order>/", SecurityQuestionDeleteView.as_view(), name="security_question_delete"),
]
