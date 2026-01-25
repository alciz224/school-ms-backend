# domain/accounts/api/urls.py

"""
URLs pour l'API accounts.
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
    # Security
    SecurityQuestionsConfigView,
    UserSecurityQuestionsView,
    SecurityQuestionsSetupView,
    SecurityQuestionsVerifyView,
)

app_name = "accounts"

urlpatterns = [
    # =========================================================================
    # AUTH
    # =========================================================================
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # =========================================================================
    # USER / PROFILE
    # =========================================================================
    path("me/", MeView.as_view(), name="me"),
    path("me/email/", UpdateEmailView.as_view(), name="update_email"),
    path("me/phone/", UpdatePhoneView.as_view(), name="update_phone"),
    # =========================================================================
    # VERIFICATION
    # =========================================================================
    path("verify/send/", SendVerificationCodeView.as_view(), name="verify_send"),
    path(
        "verify/confirm/", ConfirmVerificationCodeView.as_view(), name="verify_confirm"
    ),
    path("verify/status/", VerificationStatusView.as_view(), name="verify_status"),
    # =========================================================================
    # PASSWORD
    # =========================================================================
    path("password/reset/", PasswordResetRequestView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    # =========================================================================
    # SECURITY QUESTIONS
    # =========================================================================
    path(
        "security/questions/",
        SecurityQuestionsConfigView.as_view(),
        name="security_questions",
    ),
    path(
        "security/questions/mine/",
        UserSecurityQuestionsView.as_view(),
        name="security_questions_mine",
    ),
    path(
        "security/questions/setup/",
        SecurityQuestionsSetupView.as_view(),
        name="security_questions_setup",
    ),
    path(
        "security/questions/verify/",
        SecurityQuestionsVerifyView.as_view(),
        name="security_questions_verify",
    ),
]
