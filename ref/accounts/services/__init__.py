# domain/accounts/services/__init__.py

"""
Services du module accounts.
"""

from .auth import AuthService, AuthResult, TokenPair
from .verification import VerificationService, SendCodeResult, VerifyCodeResult
from .password import PasswordService, PasswordResetRequestResult, PasswordChangeResult
from .security import (
    SecurityService,
    SecurityQuestionsConfig,
    SecurityQuestionsSetupResult,
)

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
]
