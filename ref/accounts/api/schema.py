# domain/accounts/api/schema.py

"""
Annotations OpenAPI pour la documentation.
"""

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiExample
from drf_spectacular.types import OpenApiTypes


# Exemples de réponses
REGISTER_SUCCESS_EXAMPLE = {
    "success": True,
    "message": "Compte créé avec succès",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "phone": "+224620123456",
            "first_name": "Mamadou",
            "last_name": "Diallo",
            "full_name": "Mamadou Diallo",
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        },
        "requires_verification": True,
        "verification_sent_to": "email",
    },
}

LOGIN_SUCCESS_EXAMPLE = {
    "success": True,
    "message": "Connexion réussie",
    "data": {
        "user": {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "email": "user@example.com",
            "full_name": "Mamadou Diallo",
        },
        "tokens": {
            "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
            "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
        },
        "requires_verification": False,
    },
}

ERROR_EXAMPLE = {
    "success": False,
    "message": "Erreur de validation",
    "error": {
        "code": "VALIDATION_ERROR",
        "details": {"email": ["Cet email est déjà utilisé"]},
    },
}
