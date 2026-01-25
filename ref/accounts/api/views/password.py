# domain/accounts/api/views/password.py

"""
Views pour la gestion des mots de passe.
"""

import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from domain.accounts.services import PasswordService

from ..serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
)
from ..throttling import PasswordResetRateThrottle
from .base import APIResponseMixin

logger = logging.getLogger(__name__)


class PasswordResetRequestView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/password/reset/

    Demander une réinitialisation de mot de passe.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password_service = PasswordService()

        result = password_service.request_reset(
            identifier=serializer.validated_data["identifier"]
        )

        # Toujours la même réponse (sécurité)
        return self.success_response(
            data={
                "expires_in": result.expires_in,
                "next_step": result.next_step,
            },
            message="Si un compte existe avec cet identifiant, vous recevrez un code",
        )


class PasswordResetConfirmView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/password/reset/confirm/

    Confirmer la réinitialisation avec le code.
    """

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password_service = PasswordService()

        result = password_service.confirm_reset(
            identifier=serializer.validated_data["identifier"],
            code=serializer.validated_data["code"],
            new_password=serializer.validated_data["new_password"],
        )

        return self.success_response(
            data={
                "can_login": result.can_login,
            },
            message="Mot de passe modifié avec succès",
        )


class PasswordChangeView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/password/change/

    Changer son mot de passe (connecté).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password_service = PasswordService()

        result = password_service.change_password(
            user=request.user,
            current_password=serializer.validated_data["current_password"],
            new_password=serializer.validated_data["new_password"],
        )

        return self.success_response(
            data={
                "tokens": {
                    "access": result.access_token,
                    "refresh": result.refresh_token,
                }
            },
            message="Mot de passe modifié",
        )
