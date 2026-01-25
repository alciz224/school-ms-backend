# domain/accounts/api/exceptions.py

"""
Gestionnaire d'exceptions personnalisé pour l'API.
Formate toutes les réponses d'erreur selon le contrat.
"""

import logging
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import (
    ValidationError as DRFValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    Throttled,
)
from django.core.exceptions import ValidationError as DjangoValidationError

from domain.accounts.exceptions import AccountsException

logger = logging.getLogger(__name__)


def custom_exception_handler(exc, context):
    """
    Gestionnaire d'exceptions personnalisé.

    Formate toutes les erreurs selon le contrat API:
    {
        "success": false,
        "message": "...",
        "error": {
            "code": "...",
            "details": {...}
        }
    }
    """
    # Appeler le handler par défaut d'abord
    response = exception_handler(exc, context)

    # Gérer nos exceptions personnalisées
    if isinstance(exc, AccountsException):
        return Response(exc.to_dict(), status=exc.status_code)

    # Gérer les erreurs de validation DRF
    if isinstance(exc, DRFValidationError):
        return Response(
            {
                "success": False,
                "message": "Erreur de validation",
                "error": {"code": "VALIDATION_ERROR", "details": exc.detail},
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Gérer les erreurs d'authentification
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        return Response(
            {
                "success": False,
                "message": (
                    str(exc.detail)
                    if hasattr(exc, "detail")
                    else "Authentification requise"
                ),
                "error": {"code": "AUTH_REQUIRED", "details": None},
            },
            status=status.HTTP_401_UNAUTHORIZED,
        )

    # Gérer les erreurs de permission
    if isinstance(exc, PermissionDenied):
        return Response(
            {
                "success": False,
                "message": "Accès refusé",
                "error": {"code": "PERMISSION_DENIED", "details": None},
            },
            status=status.HTTP_403_FORBIDDEN,
        )

    # Gérer le throttling
    if isinstance(exc, Throttled):
        return Response(
            {
                "success": False,
                "message": f"Trop de requêtes. Réessayez dans {exc.wait} secondes.",
                "error": {
                    "code": "RATE_LIMIT_EXCEEDED",
                    "details": {"retry_after": exc.wait},
                },
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # Gérer les erreurs Django
    if isinstance(exc, DjangoValidationError):
        return Response(
            {
                "success": False,
                "message": "Erreur de validation",
                "error": {
                    "code": "VALIDATION_ERROR",
                    "details": (
                        exc.message_dict
                        if hasattr(exc, "message_dict")
                        else {"__all__": exc.messages}
                    ),
                },
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Pour les autres erreurs, utiliser la réponse par défaut si disponible
    if response is not None:
        custom_response_data = {
            "success": False,
            "message": "Une erreur est survenue",
            "error": {"code": "SERVER_ERROR", "details": response.data},
        }
        response.data = custom_response_data
        return response

    # Erreur non gérée
    logger.exception(f"Erreur non gérée: {exc}")
    return Response(
        {
            "success": False,
            "message": "Une erreur interne est survenue",
            "error": {"code": "SERVER_ERROR", "details": None},
        },
        status=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
