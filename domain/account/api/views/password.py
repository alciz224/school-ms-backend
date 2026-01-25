"""
Password management views.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from .base import BaseAPIView
from ..serializers import (
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    PasswordChangeSerializer,
    PasswordStrengthSerializer,
)
from ..throttling import PasswordResetRateThrottle
from domain.account.services import PasswordService


class PasswordResetRequestView(BaseAPIView):
    """Request password reset."""

    permission_classes = [AllowAny]
    throttle_classes = [PasswordResetRateThrottle]

    @extend_schema(
        tags=["Password"],
        summary="Request password reset",
        request=PasswordResetRequestSerializer,
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        password_service = PasswordService()
        result = password_service.request_reset(
            identifier=serializer.validated_data["identifier"]
        )

        return self.success_response(
            data={
                "expires_in": result.expires_in,
                "next_step": result.next_step,
            },
            message="If an account exists with this identifier, a reset code has been sent.",
        )


class PasswordResetConfirmView(BaseAPIView):
    """Confirm password reset with code."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Password"],
        summary="Confirm password reset",
        request=PasswordResetConfirmSerializer,
    )
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
            data={"can_login": result.can_login},
            message="Password reset successfully. You can now login with your new password.",
        )


class PasswordChangeView(BaseAPIView):
    """Change password for authenticated user."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Password"],
        summary="Change password",
        request=PasswordChangeSerializer,
    )
    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data, context={"request": request}
        )
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
            message="Password changed successfully.",
        )


class PasswordStrengthView(BaseAPIView):
    """Check password strength."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Password"],
        summary="Check password strength",
        request=PasswordStrengthSerializer,
    )
    def post(self, request):
        serializer = PasswordStrengthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        return self.success_response(data=serializer.validated_data)
