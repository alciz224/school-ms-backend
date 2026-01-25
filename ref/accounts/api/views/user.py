# domain/accounts/api/views/user.py

"""
Views pour le profil utilisateur.
"""

import logging
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from domain.accounts.services import VerificationService

from ..serializers import (
    UserSerializer,
    UserUpdateSerializer,
    UserEmailUpdateSerializer,
    UserPhoneUpdateSerializer,
)
from .base import APIResponseMixin

logger = logging.getLogger(__name__)


class MeView(APIResponseMixin, APIView):
    """
    GET /api/v1/auth/me/     - Récupérer mon profil
    PATCH /api/v1/auth/me/   - Modifier mon profil
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return self.success_response(data=serializer.data)

    def patch(self, request):
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        # Retourner le profil complet mis à jour
        return self.success_response(
            data=UserSerializer(request.user).data, message="Profil mis à jour"
        )


class UpdateEmailView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/me/email/

    Ajouter ou modifier son email.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserEmailUpdateSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_email = serializer.validated_data["email"]

        # Mettre à jour l'email
        user.update_email(new_email)

        # Envoyer le code de vérification
        verification_sent = False
        try:
            verification_service = VerificationService()
            verification_service.send_code(user, "email")
            verification_sent = True
        except Exception as e:
            logger.warning(f"Échec envoi vérification email: {e}")

        return self.success_response(
            data={
                "email": user.email,
                "email_verified": user.email_verified,
                "verification_sent": verification_sent,
            },
            message="Email modifié. Vérification requise.",
        )


class UpdatePhoneView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/me/phone/

    Ajouter ou modifier son téléphone.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = UserPhoneUpdateSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_phone = serializer.validated_data["phone"]

        # Mettre à jour le téléphone
        user.update_phone(new_phone)

        # Envoyer le code de vérification
        verification_sent = False
        try:
            verification_service = VerificationService()
            verification_service.send_code(user, "phone")
            verification_sent = True
        except Exception as e:
            logger.warning(f"Échec envoi vérification phone: {e}")

        return self.success_response(
            data={
                "phone": user.phone,
                "phone_verified": user.phone_verified,
                "verification_sent": verification_sent,
            },
            message="Téléphone modifié. Vérification requise.",
        )
