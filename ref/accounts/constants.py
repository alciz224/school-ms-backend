# apps/accounts/constants.py

"""
Constantes pour l'application accounts.
"""

from django.db import models


class VerificationType(models.TextChoices):
    """Type de vérification."""

    EMAIL = "email", "Email"
    PHONE = "phone", "Téléphone"
    SECURITY = "security", "Questions de sécurité"


class VerificationPurpose(models.TextChoices):
    """But de la vérification."""

    ACCOUNT_VERIFICATION = "verify", "Vérification de compte"
    PASSWORD_RESET = "reset", "Réinitialisation mot de passe"
    LOGIN_OTP = "login", "Connexion OTP"
    PHONE_CHANGE = "phone_change", "Changement de téléphone"
    EMAIL_CHANGE = "email_change", "Changement email"


class PhoneRemovalReason(models.TextChoices):
    """Raison du retrait d'un numéro."""

    CHANGED = "changed", "Changé pour un nouveau"
    LOST = "lost", "Perdu / Plus accès"
    REMOVED = "removed", "Retiré volontairement"
    REPLACED = "replaced", "Remplacé par l'utilisateur"


class LoginFailureReason(models.TextChoices):
    """Raison d'échec de connexion."""

    INVALID_CREDENTIALS = "invalid_credentials", "Identifiants invalides"
    ACCOUNT_DISABLED = "account_disabled", "Compte désactivé"
    ACCOUNT_LOCKED = "account_locked", "Compte verrouillé"
    NOT_FOUND = "not_found", "Compte non trouvé"


class SecurityLevel(models.TextChoices):
    """Niveau de sécurité du compte."""

    LOW = "low", "Faible"
    MEDIUM = "medium", "Moyen"
    HIGH = "high", "Élevé"


# Questions de sécurité prédéfinies (adaptées au contexte guinéen)
PREDEFINED_SECURITY_QUESTIONS = [
    # Contexte scolaire
    "Quel est le nom de votre école primaire ?",
    "Quel est le nom de votre professeur préféré ?",
    "Dans quelle ville avez-vous passé le CEE ?",
    # Contexte familial
    "Quel est le prénom de votre mère ?",
    "Quel est le nom de votre quartier d'enfance ?",
    "Quel est le prénom de votre grand-père paternel ?",
    # Contexte personnel
    "Quel est votre plat traditionnel préféré ?",
    "Quel est le nom de votre meilleur ami d'enfance ?",
    "Quel est le nom du marché le plus proche de chez vous ?",
    "Quel est le nom de votre mosquée ou église de quartier ?",
]
