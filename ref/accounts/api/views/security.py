# domain/accounts/api/views/security.py

"""
Views pour les questions de sécurité.
"""

import logging
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated

from domain.accounts.services import SecurityService
from domain.accounts.exceptions import (
    SecurityQuestionsRequiredError,
    SecurityAnswersInvalidError,
    SecurityMaxAttemptsError,
)

from ..serializers import (
    SecurityQuestionsConfigSerializer,
    UserSecurityQuestionsSerializer,
    SecurityQuestionsSetupSerializer,
    SecurityQuestionsVerifySerializer,
)
from ..throttling import SecurityQuestionsRateThrottle
from .base import APIResponseMixin

logger = logging.getLogger(__name__)


class SecurityQuestionsConfigView(APIResponseMixin, APIView):
    """
    GET /api/v1/auth/security/questions/

    Liste des questions prédéfinies.
    """

    permission_classes = [AllowAny]

    def get(self, request):
        security_service = SecurityService()
        config = security_service.get_questions_config()

        return self.success_response(
            data={
                "predefined_questions": config.predefined_questions,
                "min_required": config.min_required,
                "max_allowed": config.max_allowed,
                "allow_custom": config.allow_custom,
            }
        )


class UserSecurityQuestionsView(APIResponseMixin, APIView):
    """
    GET /api/v1/auth/security/questions/mine/

    Mes questions configurées (sans réponses).
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        security_service = SecurityService()
        user_questions = security_service.get_user_questions(request.user)

        return self.success_response(
            data={
                "configured_count": user_questions.configured_count,
                "questions": user_questions.questions,
            }
        )


class SecurityQuestionsSetupView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/security/questions/setup/

    Configurer ses questions de sécurité.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = SecurityQuestionsSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        security_service = SecurityService()

        result = security_service.setup_questions(
            user=request.user, questions=serializer.validated_data["questions"]
        )

        return self.success_response(
            data={
                "configured_count": result.configured_count,
                "security": {
                    "score": result.security_score,
                    "level": result.security_level,
                },
            },
            message="Questions de sécurité configurées",
        )


class SecurityQuestionsVerifyView(APIResponseMixin, APIView):
    """
    POST /api/v1/auth/security/questions/verify/

    Vérifier les réponses aux questions (récupération compte).
    """

    permission_classes = [AllowAny]
    throttle_classes = [SecurityQuestionsRateThrottle]

    def post(self, request):
        serializer = SecurityQuestionsVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        security_service = SecurityService()

        try:
            result = security_service.verify_answers(
                identifier=serializer.validated_data["identifier"],
                answers=serializer.validated_data["answers"],
                ip_address=self.get_client_ip(request),
            )

            return self.success_response(
                data={
                    "reset_token": result.reset_token,
                    "expires_in": result.expires_in,
                },
                message="Vérification réussie",
            )

        except SecurityQuestionsRequiredError as e:
            return self.error_response(
                message=e.message, code=e.code, status_code=e.status_code
            )

        except SecurityAnswersInvalidError as e:
            return self.error_response(
                message=e.message,
                code=e.code,
                details=e.details,
                status_code=e.status_code,
            )

        except SecurityMaxAttemptsError as e:
            return self.error_response(
                message=e.message, code=e.code, status_code=e.status_code
            )

        except Exception as e:
            logger.exception(f"Erreur verify_answers: {e}")
            return self.error_response(
                message="Une erreur est survenue", code="SERVER_ERROR", status_code=500
            )
