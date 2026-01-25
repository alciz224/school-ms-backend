# domain/accounts/exceptions.py

"""
Exceptions personnalisées pour le module accounts.
Mappées aux codes d'erreur définis dans les contrats API.
"""

from typing import Any


class AccountsException(Exception):
    """Exception de base pour le module accounts."""

    default_message = "Une erreur est survenue"
    default_code = "SERVER_ERROR"
    default_status_code = 400

    def __init__(
        self,
        message: str = None,
        code: str = None,
        details: dict = None,
        status_code: int = None,
    ):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.details = details
        self.status_code = status_code or self.default_status_code
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convertit l'exception en format de réponse API."""
        return {
            "success": False,
            "message": self.message,
            "error": {"code": self.code, "details": self.details},
        }


# =============================================================================
# AUTHENTIFICATION
# =============================================================================


class InvalidCredentialsError(AccountsException):
    """Identifiants incorrects."""

    default_message = "Email/téléphone ou mot de passe incorrect"
    default_code = "AUTH_INVALID_CREDENTIALS"
    default_status_code = 401


class AccountDisabledError(AccountsException):
    """Compte désactivé."""

    default_message = "Ce compte a été désactivé"
    default_code = "AUTH_ACCOUNT_DISABLED"
    default_status_code = 403


class AccountLockedError(AccountsException):
    """Compte verrouillé après trop de tentatives."""

    default_message = "Compte temporairement verrouillé"
    default_code = "AUTH_ACCOUNT_LOCKED"
    default_status_code = 423

    def __init__(self, locked_until=None, remaining_minutes: int = None, **kwargs):
        super().__init__(**kwargs)
        self.details = {
            "locked_until": locked_until.isoformat() if locked_until else None,
            "remaining_minutes": remaining_minutes,
        }


class AuthenticationRequiredError(AccountsException):
    """Authentification requise."""

    default_message = "Authentification requise"
    default_code = "AUTH_REQUIRED"
    default_status_code = 401


# =============================================================================
# INSCRIPTION
# =============================================================================


class EmailAlreadyExistsError(AccountsException):
    """Email déjà utilisé."""

    default_message = "Cet email est déjà utilisé"
    default_code = "REGISTER_EMAIL_EXISTS"
    default_status_code = 400


class PhoneAlreadyExistsError(AccountsException):
    """Téléphone déjà utilisé."""

    default_message = "Ce numéro de téléphone est déjà utilisé"
    default_code = "REGISTER_PHONE_EXISTS"
    default_status_code = 400


class InvalidRegistrationDataError(AccountsException):
    """Données d'inscription invalides."""

    default_message = "Données d'inscription invalides"
    default_code = "REGISTER_INVALID_DATA"
    default_status_code = 400


# =============================================================================
# VÉRIFICATION
# =============================================================================


class VerificationCodeInvalidError(AccountsException):
    """Code de vérification incorrect."""

    default_message = "Code de vérification incorrect"
    default_code = "VERIFY_CODE_INVALID"
    default_status_code = 400

    def __init__(self, attempts_remaining: int = None, **kwargs):
        super().__init__(**kwargs)
        if attempts_remaining is not None:
            self.details = {"attempts_remaining": attempts_remaining}


class VerificationCodeExpiredError(AccountsException):
    """Code de vérification expiré."""

    default_message = "Le code de vérification a expiré"
    default_code = "VERIFY_CODE_EXPIRED"
    default_status_code = 400


class VerificationMaxAttemptsError(AccountsException):
    """Trop de tentatives de vérification."""

    default_message = "Trop de tentatives. Demandez un nouveau code."
    default_code = "VERIFY_MAX_ATTEMPTS"
    default_status_code = 429


class AlreadyVerifiedError(AccountsException):
    """Contact déjà vérifié."""

    default_message = "Ce contact est déjà vérifié"
    default_code = "VERIFY_ALREADY_VERIFIED"
    default_status_code = 400


class NoContactToVerifyError(AccountsException):
    """Aucun contact à vérifier."""

    default_message = "Aucun contact de ce type à vérifier"
    default_code = "VERIFY_NO_CONTACT"
    default_status_code = 400


class VerificationCooldownError(AccountsException):
    """Cooldown avant nouvel envoi."""

    default_message = "Veuillez attendre avant de demander un nouveau code"
    default_code = "VERIFY_COOLDOWN"
    default_status_code = 429

    def __init__(self, retry_after: int = None, **kwargs):
        super().__init__(**kwargs)
        if retry_after is not None:
            self.details = {"retry_after": retry_after}


# =============================================================================
# MOT DE PASSE
# =============================================================================


class InvalidCurrentPasswordError(AccountsException):
    """Mot de passe actuel incorrect."""

    default_message = "Le mot de passe actuel est incorrect"
    default_code = "PASSWORD_INVALID_CURRENT"
    default_status_code = 400


class WeakPasswordError(AccountsException):
    """Mot de passe trop faible."""

    default_message = "Le mot de passe ne respecte pas les critères de sécurité"
    default_code = "PASSWORD_TOO_WEAK"
    default_status_code = 400

    def __init__(self, issues: list = None, **kwargs):
        super().__init__(**kwargs)
        if issues:
            self.details = {"issues": issues}


class PasswordResetInvalidError(AccountsException):
    """Token de réinitialisation invalide."""

    default_message = "Lien de réinitialisation invalide"
    default_code = "PASSWORD_RESET_INVALID"
    default_status_code = 400


class PasswordResetExpiredError(AccountsException):
    """Token de réinitialisation expiré."""

    default_message = "Le lien de réinitialisation a expiré"
    default_code = "PASSWORD_RESET_EXPIRED"
    default_status_code = 400


# =============================================================================
# SÉCURITÉ
# =============================================================================


class SecurityQuestionsRequiredError(AccountsException):
    """Questions de sécurité requises."""

    default_message = "Veuillez configurer vos questions de sécurité"
    default_code = "SECURITY_QUESTIONS_REQUIRED"
    default_status_code = 400


class SecurityAnswersInvalidError(AccountsException):
    """Réponses aux questions de sécurité incorrectes."""

    default_message = "Les réponses aux questions de sécurité sont incorrectes"
    default_code = "SECURITY_ANSWERS_INVALID"
    default_status_code = 400

    def __init__(self, attempts_remaining: int = None, **kwargs):
        super().__init__(**kwargs)
        if attempts_remaining is not None:
            self.details = {"attempts_remaining": attempts_remaining}


class SecurityMaxAttemptsError(AccountsException):
    """Trop de tentatives sur les questions de sécurité."""

    default_message = "Trop de tentatives. Veuillez réessayer plus tard."
    default_code = "SECURITY_MAX_ATTEMPTS"
    default_status_code = 429


# =============================================================================
# VALIDATION
# =============================================================================


class ValidationError(AccountsException):
    """Erreur de validation générale."""

    default_message = "Erreur de validation"
    default_code = "VALIDATION_ERROR"
    default_status_code = 400

    def __init__(self, field_errors: dict = None, **kwargs):
        super().__init__(**kwargs)
        if field_errors:
            self.details = field_errors


class InvalidPhoneFormatError(AccountsException):
    """Format de téléphone invalide."""

    default_message = "Le format du numéro de téléphone est invalide"
    default_code = "INVALID_PHONE_FORMAT"
    default_status_code = 400


class InvalidEmailFormatError(AccountsException):
    """Format d'email invalide."""

    default_message = "Le format de l'email est invalide"
    default_code = "INVALID_EMAIL_FORMAT"
    default_status_code = 400


# =============================================================================
# GÉNÉRAL
# =============================================================================


class NotFoundError(AccountsException):
    """Ressource non trouvée."""

    default_message = "Ressource non trouvée"
    default_code = "NOT_FOUND"
    default_status_code = 404


class RateLimitExceededError(AccountsException):
    """Rate limit dépassé."""

    default_message = "Trop de requêtes. Veuillez réessayer plus tard."
    default_code = "RATE_LIMIT_EXCEEDED"
    default_status_code = 429


class ServerError(AccountsException):
    """Erreur serveur."""

    default_message = "Une erreur interne est survenue"
    default_code = "SERVER_ERROR"
    default_status_code = 500
