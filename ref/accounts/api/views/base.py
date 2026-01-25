# domain/accounts/api/views/base.py

"""
Mixins et utilitaires pour les views.
"""

from rest_framework.response import Response
from rest_framework import status


class APIResponseMixin:
    """Mixin pour formater les réponses selon le contrat API."""

    def success_response(self, data=None, message=None, status_code=status.HTTP_200_OK):
        """Retourne une réponse de succès formatée."""
        return Response(
            {"success": True, "message": message, "data": data}, status=status_code
        )

    def created_response(self, data=None, message="Ressource créée"):
        """Retourne une réponse de création (201)."""
        return self.success_response(
            data=data, message=message, status_code=status.HTTP_201_CREATED
        )

    def error_response(
        self,
        message="Une erreur est survenue",
        code="ERROR",
        details=None,
        status_code=status.HTTP_400_BAD_REQUEST,
    ):
        """Retourne une réponse d'erreur formatée."""
        return Response(
            {
                "success": False,
                "message": message,
                "error": {"code": code, "details": details},
            },
            status=status_code,
        )

    def get_client_ip(self, request):
        """Récupère l'adresse IP du client."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0].strip()
        else:
            ip = request.META.get("REMOTE_ADDR", "0.0.0.0")
        return ip

    def get_user_agent(self, request):
        """Récupère le User-Agent."""
        return request.META.get("HTTP_USER_AGENT", "")
