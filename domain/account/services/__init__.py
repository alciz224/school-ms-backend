"""
Services for the accounts module.
"""

from .auth import AuthService, AuthResult, TokenPair
from .verification import VerificationService, SendCodeResult, VerifyCodeResult
from .password import PasswordService, PasswordResetRequestResult, PasswordChangeResult
from .security import (
    SecurityService,
    SecurityQuestionsConfig,
    SecurityQuestionsSetupResult,
)
from .parent_child import ParentChildService
from .admin_user import AdminUserService

__all__ = [
    # Auth
    "AuthService",
    "AuthResult",
    "TokenPair",
    # Verification
    "VerificationService",
    "SendCodeResult",
    "VerifyCodeResult",
    # Password
    "PasswordService",
    "PasswordResetRequestResult",
    "PasswordChangeResult",
    # Security
    "SecurityService",
    "SecurityQuestionsConfig",
    "SecurityQuestionsSetupResult",
    # Parent-Child
    "ParentChildService",
    "AdminUserService",
]
