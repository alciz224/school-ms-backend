"""
Verification views.
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


class RequestVerificationView(BaseAPIView):
    """Request a verification code."""

    permission_classes = [IsAuthenticated]
    throttle_classes = [VerificationRateThrottle]

    @extend_schema(
        tags=["Verification"],
        summary="Request verification code",
        request=SendVerificationCodeSerializer,
    )
    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
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
            message=f"Verification code sent to your {serializer.validated_data['type']}.",
        )


class VerifyCodeView(BaseAPIView):
    """Verify email or phone with code."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Verification"],
        summary="Verify code",
        request=ConfirmVerificationCodeSerializer,
    )
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
                "verified_type": result.verified_type,
                "verified_at": result.verified_at.isoformat(),
                "is_fully_verified": result.is_fully_verified,
                "security_score": result.security_score,
                "security_level": result.security_level,
            },
            message=f"Your {result.verified_type} has been verified successfully.",
        )


class VerificationStatusView(BaseAPIView):
    """Get verification status."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Verification"],
        summary="Get verification status",
    )
    def get(self, request):
        verification_service = VerificationService()
        status = verification_service.get_verification_status(request.user)

        return self.success_response(data=status)
