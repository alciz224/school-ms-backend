# domain/accounts/api/views/verification.py

"""
Views pour la vérification.
"""

import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from domain.accounts.services import VerificationService

from ..serializers import (
    SendVerificationCodeSerializer,
    ConfirmVerificationCodeSerializer,
)
from ..throttling import VerificationRateThrottle
from .base import APIResponseMixin

logger = logging.getLogger(__name__)


class SendVerificationCodeView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/verify/send/

    Envoyer un code de vérification.
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [VerificationRateThrottle]

    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_service = VerificationService()

        result = verification_service.send_code(
            user=request.user, verification_type=serializer.validated_data["type"]
        )

        response_data = {
            "sent_to": result.masked,  # Toujours masqué
            "masked": result.masked,
            "expires_in": result.expires_in,
            "can_resend_in": result.can_resend_in,
        }

        # En dev, inclure le code
        if result.dev_code:
            response_data["dev_code"] = result.dev_code

        return self.success_response(data=response_data, message="Code envoyé")


class ConfirmVerificationCodeView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/verify/confirm/

    Confirmer un code de vérification.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ConfirmVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_service = VerificationService()

        result = verification_service.verify_code(
            user=request.user,
            code=serializer.validated_data["code"],
            verification_type=serializer.validated_data["type"],
        )

        return self.success_response(
            data={
                "type": result.verified_type,
                "verified_at": result.verified_at.isoformat(),
                "is_fully_verified": result.is_fully_verified,
                "security": {
                    "score": result.security_score,
                    "level": result.security_level,
                },
            },
            message="Vérification réussie",
        )


class VerificationStatusView(APIResponseMixin, APIView):
    """
    GET /api/v1/auth/verify/status/

    Statut de vérification du compte.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        verification_service = VerificationService()
        status_data = verification_service.get_verification_status(request.user)

        return self.success_response(data=status_data)
