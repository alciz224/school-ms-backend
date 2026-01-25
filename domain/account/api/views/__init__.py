"""
Views for the accounts API.
"""

from .auth import (
    RegisterView,
    LoginView,
    LogoutView,
    TokenRefreshView,
)
from .user import (
    MeView,
    UpdateEmailView,
    UpdatePhoneView,
)
from .verification import (
    RequestVerificationView,
    VerifyCodeView,
    VerificationStatusView,
)
from .password import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
    PasswordStrengthView,
)
from .security import (
    SecurityQuestionsListView,
    SecurityQuestionsConfigView,
    SecurityQuestionsSetupView,
    SecurityQuestionDeleteView,
    SecurityQuestionsVerifyView,
)

__all__ = [
    # Auth
    "RegisterView",
    "LoginView",
    "LogoutView",
    "TokenRefreshView",
    # User
    "MeView",
    "UpdateEmailView",
    "UpdatePhoneView",
    # Verification
    "RequestVerificationView",
    "VerifyCodeView",
    "VerificationStatusView",
    # Password
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "PasswordChangeView",
    "PasswordStrengthView",
    # Security
    "SecurityQuestionsListView",
    "SecurityQuestionsConfigView",
    "SecurityQuestionsSetupView",
    "SecurityQuestionDeleteView",
    "SecurityQuestionsVerifyView",
]
