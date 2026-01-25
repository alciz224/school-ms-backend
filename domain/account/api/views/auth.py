"""
Authentication views.
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from .base import BaseAPIView
from ..serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    TokenRefreshSerializer,
    UserSerializer,
)
from ..throttling import AuthRateThrottle, RegistrationRateThrottle
from domain.account.services import AuthService


class RegisterView(BaseAPIView):
    """Register a new user account."""

    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    @extend_schema(
        tags=["Auth"],
        summary="Register a new account",
        request=RegisterSerializer,
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()
        result = auth_service.register(
            email=serializer.validated_data.get("email"),
            phone=serializer.validated_data.get("phone"),
            password=serializer.validated_data["password"],
            first_name=serializer.validated_data["first_name"],
            last_name=serializer.validated_data["last_name"],
            request_meta={
                "ip_address": self.get_client_ip(),
                "user_agent": self.get_user_agent(),
            },
        )

        return self.success_response(
            data={
                "user": UserSerializer(result.user).data,
                "tokens": {
                    "access": result.tokens.access,
                    "refresh": result.tokens.refresh,
                },
                "requires_verification": result.requires_verification,
                "verification_sent_to": result.verification_sent_to,
            },
            message="Account created successfully. Please verify your email or phone.",
            status=status.HTTP_201_CREATED,
        )


class LoginView(BaseAPIView):
    """Login with email or phone."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    @extend_schema(
        tags=["Auth"],
        summary="Login",
        request=LoginSerializer,
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()
        result = auth_service.login(
            identifier=serializer.validated_data["identifier"],
            password=serializer.validated_data["password"],
            ip_address=self.get_client_ip(),
            user_agent=self.get_user_agent(),
        )

        return self.success_response(
            data={
                "user": UserSerializer(result.user).data,
                "tokens": {
                    "access": result.tokens.access,
                    "refresh": result.tokens.refresh,
                },
                "requires_verification": result.requires_verification,
            },
            message="Login successful.",
        )


class LogoutView(BaseAPIView):
    """Logout by blacklisting refresh token."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Auth"],
        summary="Logout",
        request=LogoutSerializer,
    )
    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()
        auth_service.logout(serializer.validated_data["refresh"])

        return self.success_response(message="Logged out successfully.")


class TokenRefreshView(BaseAPIView):
    """Refresh access token."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Auth"],
        summary="Refresh token",
        request=TokenRefreshSerializer,
    )
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()
        tokens = auth_service.refresh_tokens(serializer.validated_data["refresh"])

        return self.success_response(
            data={
                "access": tokens.access,
                "refresh": tokens.refresh,
            }
        )
