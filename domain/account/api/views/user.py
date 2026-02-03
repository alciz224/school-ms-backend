"""
User management views.

API Contract: See API_ENDPOINTS.md section 3
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
    """
    Get or update current user's profile.
    
    GET /api/auth/me/
    PATCH /api/auth/me/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User Profile"],
        summary="Get current user profile",
    )
    def get(self, request):
        serializer = UserDetailSerializer(request.user)
        return self.success_response(data=serializer.data)

    @extend_schema(
        tags=["User Profile"],
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
            message="Profil mis à jour",
        )

    @extend_schema(
        tags=["User Profile"],
        summary="Update current user profile",
        request=UserUpdateSerializer,
    )
    def put(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return self.success_response(
            data=UserDetailSerializer(request.user).data,
            message="Profil mis à jour",
        )


class UpdateEmailView(BaseAPIView):
    """
    Add or change user's email address.
    
    POST /api/auth/me/email/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User Profile"],
        summary="Change email address",
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
            data={
                "email": user.email,
                "email_verified": user.email_verified,
                "verification_sent": True,
            },
            message="Email modifié. Vérification requise.",
        )


class UpdatePhoneView(BaseAPIView):
    """
    Add or change user's phone number.
    
    POST /api/auth/me/phone/
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["User Profile"],
        summary="Change phone number",
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
            data={
                "phone": user.phone,
                "phone_verified": user.phone_verified,
                "verification_sent": True,
            },
            message="Téléphone modifié. Vérification requise.",
        )
