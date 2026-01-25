# domain/accounts/api/views/__init__.py

"""
Views pour l'API accounts.
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
    SendVerificationCodeView,
    ConfirmVerificationCodeView,
    VerificationStatusView,
)
from .password import (
    PasswordResetRequestView,
    PasswordResetConfirmView,
    PasswordChangeView,
)
from .security import (
    SecurityQuestionsConfigView,
    UserSecurityQuestionsView,
    SecurityQuestionsSetupView,
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
    "SendVerificationCodeView",
    "ConfirmVerificationCodeView",
    "VerificationStatusView",
    # Password
    "PasswordResetRequestView",
    "PasswordResetConfirmView",
    "PasswordChangeView",
    # Security
    "SecurityQuestionsConfigView",
    "UserSecurityQuestionsView",
    "SecurityQuestionsSetupView",
    "SecurityQuestionsVerifyView",
]
