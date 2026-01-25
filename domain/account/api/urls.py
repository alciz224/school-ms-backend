"""
URL configuration for account API.
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
    RequestVerificationView,
    VerifyCodeView,
    VerificationStatusView,
    # Password
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
    PasswordStrengthView,
    # Security
    SecurityQuestionsListView,
    SecurityQuestionsConfigView,
    SecurityQuestionsSetupView,
    SecurityQuestionDeleteView,
    SecurityQuestionsVerifyView,
)

app_name = "account"

urlpatterns = [
    # ==========================================================================
    # AUTH
    # ==========================================================================
    path("auth/register/", RegisterView.as_view(), name="register"),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    # ==========================================================================
    # USER PROFILE
    # ==========================================================================
    path("users/me/", MeView.as_view(), name="me"),
    path("users/me/email/", UpdateEmailView.as_view(), name="update_email"),
    path("users/me/phone/", UpdatePhoneView.as_view(), name="update_phone"),

    # ==========================================================================
    # VERIFICATION
    # ==========================================================================
    path("verification/request/", RequestVerificationView.as_view(), name="request_verification"),
    path("verification/verify/", VerifyCodeView.as_view(), name="verify_code"),
    path("verification/status/", VerificationStatusView.as_view(), name="verification_status"),

    # ==========================================================================
    # PASSWORD
    # ==========================================================================
    path("password/reset/request/", PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/confirm/", PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password/strength/", PasswordStrengthView.as_view(), name="password_strength"),

    # ==========================================================================
    # SECURITY QUESTIONS
    # ==========================================================================
    path("security/questions/", SecurityQuestionsListView.as_view(), name="security_questions"),
    path("security/questions/config/", SecurityQuestionsConfigView.as_view(), name="security_config"),
    path("security/questions/setup/", SecurityQuestionsSetupView.as_view(), name="security_setup"),
    path("security/questions/<int:order>/", SecurityQuestionDeleteView.as_view(), name="security_question_delete"),
    path("security/questions/verify/", SecurityQuestionsVerifyView.as_view(), name="security_verify"),
]
