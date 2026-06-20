"""
Session-based authentication views (API v2).

This module provides session-based authentication for Next.js frontend
that only forwards session cookies without client-side cookie logic.
"""

from django.contrib.auth import login, logout
from django.middleware.csrf import get_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from .base import BaseAPIView
from ..serializers.auth_v2 import (
    SessionRegisterSerializer,
    SessionLoginSerializer,
    SessionLogoutSerializer,
    SelectRoleSerializer,
)
from ..serializers import UserSerializer
from ..throttling import AuthRateThrottle, RegistrationRateThrottle
from domain.account.services import AuthService
from domain.account.selectors import UserRoleSelector
from domain.account.constants import ACTIVE_ROLE_SESSION_KEY


class SessionRegisterView(BaseAPIView):
    """Register a new user account with session authentication."""

    permission_classes = [AllowAny]
    throttle_classes = [RegistrationRateThrottle]
    serializer_class = SessionRegisterSerializer

    @extend_schema(
        tags=["Auth V2 - Session"],
        summary="Register a new account (session-based)",
        request=SessionRegisterSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
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

        # Log the user in (create session)
        login(request, result.user, backend="domain.account.backends.EmailPhoneBackend")

        # Set default role if not already set
        if ACTIVE_ROLE_SESSION_KEY not in request.session:
            default_role = UserRoleSelector.get_default_role(result.user)
            if default_role:
                request.session[ACTIVE_ROLE_SESSION_KEY] = default_role

        # Get CSRF token for the response
        csrf_token = get_token(request)

        return self.success_response(
            data={
                "user": UserSerializer(result.user, context={'request': request}).data,
                "csrf_token": csrf_token,
                "requires_verification": result.requires_verification,
                "verification_sent_to": result.verification_sent_to,
            },
            message="Account created successfully. Please verify your email or phone.",
            status=status.HTTP_201_CREATED,
        )


class SessionLoginView(BaseAPIView):
    """Login with email or phone using session authentication."""

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]
    serializer_class = SessionLoginSerializer

    @extend_schema(
        tags=["Auth V2 - Session"],
        summary="Login (session-based)",
        request=SessionLoginSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()
        result = auth_service.login(
            identifier=serializer.validated_data["identifier"],
            password=serializer.validated_data["password"],
            ip_address=self.get_client_ip(),
            user_agent=self.get_user_agent(),
        )

        # Log the user in (create session)
        login(request, result.user, backend="domain.account.backends.EmailPhoneBackend")

        # Set default role if not already set
        if ACTIVE_ROLE_SESSION_KEY not in request.session:
            default_role = UserRoleSelector.get_default_role(result.user)
            if default_role:
                request.session[ACTIVE_ROLE_SESSION_KEY] = default_role

        # Get CSRF token for the response
        csrf_token = get_token(request)

        return self.success_response(
            data={
                "user": UserSerializer(result.user, context={'request': request}).data,
                "csrf_token": csrf_token,
                "requires_verification": result.requires_verification,
            },
            message="Login successful.",
        )


class SessionLogoutView(BaseAPIView):
    """Logout by destroying the session."""

    permission_classes = [IsAuthenticated]
    serializer_class = SessionLogoutSerializer

    @extend_schema(
        tags=["Auth V2 - Session"],
        summary="Logout (session-based)",
        request=SessionLogoutSerializer,
    )
    def post(self, request):
        # Django's logout() clears the session
        logout(request)

        return self.success_response(message="Logged out successfully.")


class SessionStatusView(BaseAPIView):
    """Check session status and get current user."""

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(
        tags=["Auth V2 - Session"],
        summary="Get session status and current user",
    )
    def get(self, request):
        res = self.success_response(
            data={
                "user": UserSerializer(request.user, context={'request': request}).data,
                "authenticated": True,
            },
            message="Session is active.",
        )
        print(f"Response data: {res.data}")
        print(f"Response status: {res.status_code}")
        return res


class CSRFTokenView(BaseAPIView):
    """Get CSRF token for session-based requests."""

    permission_classes = [AllowAny]
    serializer_class = None

    @extend_schema(
        tags=["Auth V2 - Session"],
        summary="Get CSRF token",
    )
    def get(self, request):
        # Force generation of CSRF token
        csrf_token = get_token(request)

        return self.success_response(
            data={"csrf_token": csrf_token},
            message="CSRF token generated.",
        )


class SelectRoleView(BaseAPIView):
    """Select active role for the current session."""

    permission_classes = [IsAuthenticated]
    serializer_class = SelectRoleSerializer

    @extend_schema(
        tags=["Auth V2 - Session"],
        summary="Select active role for the session",
        description="Sets the active role for the current session. The role must be available for the user.",
        request=SelectRoleSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)

        # Store the selected role in the session
        role = serializer.validated_data['role']
        request.session[ACTIVE_ROLE_SESSION_KEY] = role

        return self.success_response(
            data={"role": role},
            message="Role selected successfully."
        )
