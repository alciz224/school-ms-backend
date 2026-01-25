"""
Security question views.
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


class SecurityQuestionsListView(BaseAPIView):
    """List user's security questions."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Security"],
        summary="Get user's security questions",
    )
    def get(self, request):
        security_service = SecurityService()
        result = security_service.get_user_questions(request.user)

        return self.success_response(
            data={
                "questions": result.questions,
                "count": result.configured_count,
                "max_questions": 3,
            }
        )


class SecurityQuestionsConfigView(BaseAPIView):
    """Get security questions configuration and predefined questions."""

    permission_classes = [AllowAny]

    @extend_schema(
        tags=["Security"],
        summary="Get security questions configuration",
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


class SecurityQuestionsSetupView(BaseAPIView):
    """Setup security questions."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Security"],
        summary="Setup security questions",
        request=SecurityQuestionsSetupSerializer,
    )
    def post(self, request):
        serializer = SecurityQuestionsSetupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        security_service = SecurityService()
        result = security_service.setup_questions(
            user=request.user,
            questions=serializer.validated_data["questions"],
        )

        return self.success_response(
            data={
                "configured_count": result.configured_count,
                "security_score": result.security_score,
                "security_level": result.security_level,
            },
            message="Security questions saved successfully.",
            status=status.HTTP_201_CREATED,
        )


class SecurityQuestionDeleteView(BaseAPIView):
    """Delete a security question."""

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Security"],
        summary="Delete a security question",
    )
    def delete(self, request, order):
        deleted, _ = SecurityQuestion.objects.filter(
            user=request.user, order=order
        ).delete()

        if deleted:
            return self.success_response(message="Security question deleted.")

        return self.error_response(
            message="Security question not found.",
            code="not_found",
            status=status.HTTP_404_NOT_FOUND,
        )


class SecurityQuestionsVerifyView(BaseAPIView):
    """Verify security question answers (for account recovery)."""

    permission_classes = [AllowAny]
    throttle_classes = [SecurityQuestionsRateThrottle]

    @extend_schema(
        tags=["Security"],
        summary="Verify security question answers",
        request=SecurityQuestionsVerifySerializer,
    )
    def post(self, request):
        serializer = SecurityQuestionsVerifySerializer(data=request.data)
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
