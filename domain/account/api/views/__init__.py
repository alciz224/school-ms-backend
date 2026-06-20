"""
Views for the accounts API.

API Contract: See API_ENDPOINTS.md for full specification.
"""

from .auth import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshView,
)
from .auth_v2 import (
    SessionRegisterView,
    SessionLoginView,
    SessionLogoutView,
    SessionStatusView,
    CSRFTokenView,
)
from .user import (
    MeView,
    UpdateEmailView,
    UpdatePhoneView,
)
from .verification import (
    SendVerificationCodeView,
    ConfirmVerificationCodeView,
    VerificationStatusView,
)
from .password import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
    PasswordStrengthView,
)
from .admin_user import AdminUserViewSet
from .security import (
    PredefinedQuestionsView,
    UserSecurityQuestionsView,
    SecurityQuestionsSetupView,
    SecurityQuestionDeleteView,
    SecurityQuestionsVerifyView,
)

__all__ = [
    # Admin User
    "AdminUserViewSet",
    # Auth
    "RegisterView",
    "LoginView",
    "LogoutView",
    "TokenRefreshView",
    # Auth V2 - Session
    "SessionRegisterView",
    "SessionLoginView",
    "SessionLogoutView",
    "SessionStatusView",
    "CSRFTokenView",
    # User
    "MeView",
    "UpdateEmailView",
    "UpdatePhoneView",
    # Verification
    "SendVerificationCodeView",
    "ConfirmVerificationCodeView",
    "VerificationStatusView",
    # Password
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "PasswordChangeView",
    "PasswordStrengthView",
    # Security Questions
    "PredefinedQuestionsView",
    "UserSecurityQuestionsView",
    "SecurityQuestionsSetupView",
    "SecurityQuestionDeleteView",
    "SecurityQuestionsVerifyView",
]
