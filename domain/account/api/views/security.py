"""
Security question views.

API Contract: See API_ENDPOINTS.md section 6
"""

from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema

from .base import BaseAPIView
from ..serializers import (
    SecurityQuestionsSetupSerializer,
    SecurityQuestionsVerifySerializer,
    PredefinedQuestionsSerializer,
)
from ..throttling import SecurityQuestionsRateThrottle
from domain.account.services import SecurityService
from domain.account.models import SecurityQuestion
from domain.account.selectors import SecurityQuestionSelector


class PredefinedQuestionsView(BaseAPIView):
    """
    Get list of predefined security questions.
    
    GET /api/auth/security-questions/
    """

    permission_classes = [AllowAny]
    serializer_class = None

    @extend_schema(
        tags=["Security Questions"],
        summary="Get predefined security questions",
    )
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


class UserSecurityQuestionsView(BaseAPIView):
    """
    Get user's configured security questions (without answers).
    
    GET /api/auth/security-questions/mine/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(
        tags=["Security Questions"],
        summary="Get user's security questions",
    )
    def get(self, request):
        security_service = SecurityService()
        result = security_service.get_user_questions(request.user)

        return self.success_response(
            data={
                "configured_count": result.configured_count,
                "questions": result.questions,
            }
        )


class SecurityQuestionsSetupView(BaseAPIView):
    """
    Configure user's security questions.
    
    POST /api/auth/security-questions/setup/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = SecurityQuestionsSetupSerializer

    @extend_schema(
        tags=["Security Questions"],
        summary="Setup security questions",
        request=SecurityQuestionsSetupSerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        security_service = SecurityService()
        result = security_service.setup_questions(
            user=request.user,
            questions=serializer.validated_data["questions"],
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
            status=status.HTTP_200_OK,
        )


class SecurityQuestionDeleteView(BaseAPIView):
    """
    Delete a security question.
    
    DELETE /api/auth/security-questions/<order>/
    """

    permission_classes = [IsAuthenticated]
    serializer_class = None

    @extend_schema(
        tags=["Security Questions"],
        summary="Delete a security question",
    )
    def delete(self, request, order):
        question = SecurityQuestionSelector.for_user_by_order(
            user=request.user, order=order
        )
        if question:
            question.delete()
            return self.success_response(message="Security question deleted.")

        return self.error_response(
            message="Security question not found.",
            code="not_found",
            status=status.HTTP_404_NOT_FOUND,
        )


class SecurityQuestionsVerifyView(BaseAPIView):
    """
    Verify security question answers (for account recovery).
    
    POST /api/auth/security-questions/verify/
    """

    permission_classes = [AllowAny]
    throttle_classes = [SecurityQuestionsRateThrottle]
    serializer_class = SecurityQuestionsVerifySerializer

    @extend_schema(
        tags=["Security Questions"],
        summary="Verify security question answers",
        request=SecurityQuestionsVerifySerializer,
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        security_service = SecurityService()
        result = security_service.verify_answers(
            identifier=serializer.validated_data["identifier"],
            answers=serializer.validated_data["answers"],
            ip_address=self.get_client_ip(),
        )

        return self.success_response(
            data={
                "reset_token": result.reset_token,
                "expires_in": result.expires_in,
            },
            message="Security questions verified. You can now reset your password.",
        )
