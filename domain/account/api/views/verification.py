"""
Verification views.

API Contract: See API_ENDPOINTS.md sections 5.1-5.3
"""

from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .base import BaseAPIView
from ..serializers import (
    SendVerificationCodeSerializer,
    ConfirmVerificationCodeSerializer,
)
from ..throttling import VerificationRateThrottle
from domain.account.services import VerificationService


class SendVerificationCodeView(BaseAPIView):
    """
    Send a verification code.
    
    POST /api/auth/verify/send/
    """

    permission_classes = [IsAuthenticated]
    throttle_classes = [VerificationRateThrottle]
    serializer_class = SendVerificationCodeSerializer

    @extend_schema(
        tags=["Verification"],
        summary="Send verification code",
        request=SendVerificationCodeSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        verification_service = VerificationService()
        result = verification_service.send_code(
            user=request.user,
            verification_type=serializer.validated_data["type"],
        )

        response_data = {
            "sent_to": result.sent_to,
            "masked": result.masked,
            "expires_in": result.expires_in,
            "can_resend_in": result.can_resend_in,
        }

        # Include code in dev mode
        if result.dev_code:
            response_data["dev_code"] = result.dev_code

        return self.success_response(
            data=response_data,
            message="Code envoyé",
        )


class ConfirmVerificationCodeView(BaseAPIView):
    """
    Confirm verification with code.
    
    POST /api/auth/verify/confirm/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = ConfirmVerificationCodeSerializer

    @extend_schema(
        tags=["Verification"],
        summary="Confirm verification code",
        request=ConfirmVerificationCodeSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
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


class VerificationStatusView(BaseAPIView):
    """Get verification status."""

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(
        tags=["Verification"],
        summary="Get verification status",
    )
    def get(self, request):
        verification_service = VerificationService()
        status = verification_service.get_verification_status(request.user)

        return self.success_response(data=status)
