# domain/accounts/api/serializers/__init__.py

"""
Serializers pour l'API accounts.
"""

from .auth import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    TokenRefreshSerializer,
)
from .user import (
    UserSerializer,
    UserUpdateSerializer,
    UserEmailUpdateSerializer,
    UserPhoneUpdateSerializer,
)
from .verification import (
    SendVerificationCodeSerializer,
    ConfirmVerificationCodeSerializer,
    VerificationStatusSerializer,
)
from .password import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
)
from .security import (
    SecurityQuestionsConfigSerializer,
    SecurityQuestionSetupSerializer,
    SecurityQuestionsSetupSerializer,
    SecurityQuestionVerifyAnswerSerializer,
    SecurityQuestionsVerifySerializer,
    UserSecurityQuestionsSerializer,
)

__all__ = [
    # Auth
    "RegisterSerializer",
    "LoginSerializer",
    "LogoutSerializer",
    "TokenRefreshSerializer",
    # User
    "UserSerializer",
    "UserUpdateSerializer",
    "UserEmailUpdateSerializer",
    "UserPhoneUpdateSerializer",
    # Verification
    "SendVerificationCodeSerializer",
    "ConfirmVerificationCodeSerializer",
    "VerificationStatusSerializer",
    # Password
    "PasswordResetRequestSerializer",
    "PasswordResetConfirmSerializer",
    "PasswordChangeSerializer",
    # Security
    "SecurityQuestionsConfigSerializer",
    "SecurityQuestionSetupSerializer",
    "SecurityQuestionsSetupSerializer",
    "SecurityQuestionVerifyAnswerSerializer",
    "SecurityQuestionsVerifySerializer",
    "UserSecurityQuestionsSerializer",
]
