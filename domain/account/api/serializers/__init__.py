"""
Serializers for the accounts API.
"""

from .auth import (
    CustomTokenObtainPairSerializer,
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    TokenRefreshSerializer,
    TokenPairSerializer,
)
from .user import (
    UserSerializer,
    UserDetailSerializer,
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
    PasswordStrengthSerializer,
)
from .security import (
    SecurityQuestionsConfigSerializer,
    SecurityQuestionSetupSerializer,
    SecurityQuestionsSetupSerializer,
    SecurityQuestionVerifyAnswerSerializer,
    SecurityQuestionsVerifySerializer,
    UserSecurityQuestionsSerializer,
    PredefinedQuestionsSerializer,
)
from .admin_user import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminUserCreateSerializer,
    AdminUserUpdateSerializer,
)
from .auth_v2 import (
    SessionRegisterSerializer,
    SessionLoginSerializer,
    SessionLogoutSerializer,
    SelectRoleSerializer,
)

__all__ = [
    # Admin User
    "AdminUserListSerializer",
    "AdminUserDetailSerializer",
    "AdminUserCreateSerializer",
    "AdminUserUpdateSerializer",
    # Auth
    "RegisterSerializer",
    "LoginSerializer",
    "LogoutSerializer",
    "TokenRefreshSerializer",
    "TokenPairSerializer",
    # Auth V2
    "SessionRegisterSerializer",
    "SessionLoginSerializer",
    "SessionLogoutSerializer",
    "SelectRoleSerializer",
    # User
    "UserSerializer",
    "UserDetailSerializer",
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
    "PasswordStrengthSerializer",
    # Security
    "SecurityQuestionsConfigSerializer",
    "SecurityQuestionSetupSerializer",
    "SecurityQuestionsSetupSerializer",
    "SecurityQuestionVerifyAnswerSerializer",
    "SecurityQuestionsVerifySerializer",
    "UserSecurityQuestionsSerializer",
    "PredefinedQuestionsSerializer",
]
