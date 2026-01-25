"""
User management views.
"""

from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema

from .base import BaseAPIView
from ..serializers import (
    UserDetailSerializer,
    UserUpdateSerializer,
    UserEmailUpdateSerializer,
    UserPhoneUpdateSerializer,
)


class MeView(BaseAPIView):
    """Get or update current user's profile."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        summary="Get current user profile",
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return self.success_response(data=serializer.data)

    @extend_schema(
        tags=["Users"],
        summary="Update current user profile",
        request=UserUpdateSerializer,
    )
    def patch(self, request):
        serializer = UserUpdateSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success_response(
            data=UserDetailSerializer(request.user).data,
            message="Profile updated successfully.",
        )

    @extend_schema(
        tags=["Users"],
        summary="Update current user profile",
        request=UserUpdateSerializer,
    )
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success_response(
            data=UserDetailSerializer(request.user).data,
            message="Profile updated successfully.",
        )


class UpdateEmailView(BaseAPIView):
    """Update user's email address."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        summary="Update email address",
        request=UserEmailUpdateSerializer,
    )
    def post(self, request):
        serializer = UserEmailUpdateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.update_email(serializer.validated_data["email"])

        return self.success_response(
            data={"email": user.email, "email_verified": user.email_verified},
            message="Email updated. Please verify your new email address.",
        )


class UpdatePhoneView(BaseAPIView):
    """Update user's phone number."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Users"],
        summary="Update phone number",
        request=UserPhoneUpdateSerializer,
    )
    def post(self, request):
        serializer = UserPhoneUpdateSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        user.update_phone(serializer.validated_data["phone"])

        return self.success_response(
            data={"phone": user.phone, "phone_verified": user.phone_verified},
            message="Phone updated. Please verify your new phone number.",
        )
