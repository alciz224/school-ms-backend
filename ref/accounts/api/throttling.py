# domain/accounts/api/throttling.py

"""
Rate limiting personnalisé pour l'API accounts.
"""

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class AuthRateThrottle(AnonRateThrottle):
    """
    Rate limiting pour les endpoints d'authentification.
    5 requêtes par minute pour les anonymes.
    """

    scope = "auth"
    rate = "5/minute"


class VerificationRateThrottle(UserRateThrottle):
    """
    Rate limiting pour l'envoi de codes de vérification.
    3 requêtes par minute.
    """

    scope = "verification"
    rate = "3/minute"


class PasswordResetRateThrottle(AnonRateThrottle):
    """
    Rate limiting pour les demandes de reset password.
    3 requêtes par heure.
    """

    scope = "password_reset"
    rate = "3/hour"


class SecurityQuestionsRateThrottle(AnonRateThrottle):
    """
    Rate limiting pour la vérification des questions de sécurité.
    5 requêtes par heure.
    """

    scope = "security_questions"
    rate = "5/hour"
