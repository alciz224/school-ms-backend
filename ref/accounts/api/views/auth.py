# domain/accounts/api/views/auth.py

"""
Views pour l'authentification.
"""

import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from domain.accounts.services import AuthService
from domain.accounts.exceptions import AccountsException

from ..serializers import (
    RegisterSerializer,
    LoginSerializer,
    LogoutSerializer,
    TokenRefreshSerializer,
    UserSerializer,
)
from ..throttling import AuthRateThrottle
from .base import APIResponseMixin

logger = logging.getLogger(__name__)


class RegisterView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/register/

    Inscription d'un nouvel utilisateur.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

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
                "ip_address": self.get_client_ip(request),
                "user_agent": self.get_user_agent(request),
            },
        )

        return self.created_response(
            data={
                "user": UserSerializer(result.user).data,
                "tokens": {
                    "access": result.tokens.access,
                    "refresh": result.tokens.refresh,
                },
                "requires_verification": result.requires_verification,
                "verification_sent_to": result.verification_sent_to,
            },
            message="Compte créé avec succès",
        )


class LoginView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/login/

    Connexion utilisateur.
    """

    permission_classes = [AllowAny]
    throttle_classes = [AuthRateThrottle]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()

        result = auth_service.login(
            identifier=serializer.validated_data["identifier"],
            password=serializer.validated_data["password"],
            ip_address=self.get_client_ip(request),
            user_agent=self.get_user_agent(request),
        )

        response_data = {
            "user": UserSerializer(result.user).data,
            "tokens": {
                "access": result.tokens.access,
                "refresh": result.tokens.refresh,
            },
            "requires_verification": result.requires_verification,
        }

        # Si non vérifié, ajouter les options de vérification
        if result.requires_verification:
            verification_options = []
            if result.user.email:
                verification_options.append("email")
            if result.user.phone:
                verification_options.append("phone")
            response_data["verification_options"] = verification_options

        message = (
            "Connexion réussie"
            if not result.requires_verification
            else "Vérification requise"
        )

        return self.success_response(data=response_data, message=message)


class LogoutView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/logout/

    Déconnexion (blacklist le refresh token).
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()
        auth_service.logout(serializer.validated_data["refresh"])

        return self.success_response(data=None, message="Déconnexion réussie")


class TokenRefreshView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/token/refresh/

    Rafraîchir le token d'accès.
    """

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        auth_service = AuthService()
        tokens = auth_service.refresh_tokens(serializer.validated_data["refresh"])

        return self.success_response(
            data={
                "access": tokens.access,
                "refresh": tokens.refresh,
            },
            message="Token rafraîchi",
        )
