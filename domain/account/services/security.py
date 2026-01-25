"""
Security service.
Handles: security questions, security score.
"""

import logging
import secrets
from typing import List, Optional
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from domain.account.models import CustomUser, SecurityQuestion, SecurityQuestionAttempt
from domain.account.constants import PREDEFINED_SECURITY_QUESTIONS, VerificationPurpose
from domain.account.exceptions import (
    SecurityQuestionsRequiredError,
    SecurityAnswersInvalidError,
    SecurityMaxAttemptsError,
    ValidationError,
)

logger = logging.getLogger(__name__)


@dataclass
class SecurityQuestionsConfig:
    """Security questions configuration."""

    predefined_questions: List[str]
    min_required: int
    max_allowed: int
    allow_custom: bool


@dataclass
class UserSecurityQuestions:
    """User's security questions."""

    configured_count: int
    questions: List[dict]


@dataclass
class SecurityQuestionsSetupResult:
    """Questions setup result."""

    configured_count: int
    security_score: int
    security_level: str


@dataclass
class SecurityQuestionsVerifyResult:
    """Answers verification result."""

    success: bool
    reset_token: Optional[str]
    expires_in: int


class SecurityService:
    """Security management service."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})

    # =========================================================================
    # QUESTIONS CONFIGURATION
    # =========================================================================

    def get_questions_config(self) -> SecurityQuestionsConfig:
        """Return security questions configuration."""
        return SecurityQuestionsConfig(
            predefined_questions=PREDEFINED_SECURITY_QUESTIONS.copy(),
            min_required=self.config.get("MIN_SECURITY_QUESTIONS_FOR_RECOVERY", 2),
            max_allowed=self.config.get("MAX_SECURITY_QUESTIONS", 3),
            allow_custom=True,
        )

    def get_user_questions(self, user: CustomUser) -> UserSecurityQuestions:
        """Return user's configured questions."""
        questions = SecurityQuestion.objects.filter(user=user).order_by("order")

        return UserSecurityQuestions(
            configured_count=questions.count(),
            questions=[{"order": q.order, "question": q.question} for q in questions],
        )

    @transaction.atomic
    def setup_questions(
        self, user: CustomUser, questions: List[dict]
    ) -> SecurityQuestionsSetupResult:
        """
        Configure user's security questions.

        Args:
            user: The user
            questions: List of dicts with 'question' and 'answer'

        Returns:
            SecurityQuestionsSetupResult

        Raises:
            ValidationError: If data is invalid
        """
        min_required = self.config.get("MIN_SECURITY_QUESTIONS_FOR_RECOVERY", 2)
        max_allowed = self.config.get("MAX_SECURITY_QUESTIONS", 3)

        # Validation
        if len(questions) < min_required:
            raise ValidationError(
                message=f"At least {min_required} questions are required",
                field_errors={
                    "questions": [f"Minimum {min_required} questions required"]
                },
            )

        if len(questions) > max_allowed:
            raise ValidationError(
                message=f"Maximum {max_allowed} questions allowed",
                field_errors={
                    "questions": [f"Maximum {max_allowed} questions allowed"]
                },
            )

        # Validate each question
        for i, q in enumerate(questions):
            if not q.get("question") or len(q["question"].strip()) < 10:
                raise ValidationError(
                    message="Question must contain at least 10 characters",
                    field_errors={f"questions.{i}.question": ["Question too short"]},
                )

            if not q.get("answer") or len(q["answer"].strip()) < 2:
                raise ValidationError(
                    message="Answer must contain at least 2 characters",
                    field_errors={f"questions.{i}.answer": ["Answer too short"]},
                )

        # Delete old questions
        SecurityQuestion.objects.filter(user=user).delete()

        # Create new ones
        for i, q in enumerate(questions):
            SecurityQuestion.create_for_user(
                user=user,
                question=q["question"].strip(),
                answer=q["answer"].strip(),
                order=i + 1,
            )

        logger.info(
            f"Security questions configured for {user.identifier}: "
            f"{len(questions)} questions"
        )

        return SecurityQuestionsSetupResult(
            configured_count=len(questions),
            security_score=user.security_score,
            security_level=user.security_level,
        )

    # =========================================================================
    # ANSWERS VERIFICATION
    # =========================================================================

    @transaction.atomic
    def verify_answers(
        self, identifier: str, answers: List[dict], ip_address: str = None
    ) -> SecurityQuestionsVerifyResult:
        """
        Verify security question answers.

        Args:
            identifier: Email or phone
            answers: List of dicts with 'order' and 'answer'
            ip_address: Client IP address

        Returns:
            SecurityQuestionsVerifyResult with reset token if successful

        Raises:
            SecurityQuestionsRequiredError: If no questions configured
            SecurityAnswersInvalidError: If answers incorrect
            SecurityMaxAttemptsError: If too many attempts
        """
        # Find user
        user = CustomUser.objects.get_by_identifier(identifier.strip())

        if not user:
            # Same message to not reveal account existence
            raise SecurityAnswersInvalidError()

        # Check questions are configured
        user_questions = SecurityQuestion.objects.filter(user=user)
        if not user_questions.exists():
            raise SecurityQuestionsRequiredError()

        # Check rate limiting
        if self._is_attempts_locked(user, ip_address):
            raise SecurityMaxAttemptsError()

        # Verify answers
        min_correct = self.config.get("MIN_SECURITY_QUESTIONS_FOR_RECOVERY", 2)
        correct_count = 0

        for answer_data in answers:
            order = answer_data.get("order")
            answer = answer_data.get("answer", "")

            question = user_questions.filter(order=order).first()
            if question and question.check_answer(answer):
                correct_count += 1

        # Record attempt
        attempt = SecurityQuestionAttempt.objects.create(
            user=user,
            ip_address=ip_address,
            questions_answered=len(answers),
            correct_answers=correct_count,
            success=correct_count >= min_correct,
        )

        if correct_count < min_correct:
            remaining = self._get_remaining_attempts(user)
            if remaining <= 0:
                raise SecurityMaxAttemptsError()
            raise SecurityAnswersInvalidError(attempts_remaining=remaining)

        # Success - generate temporary token
        reset_token = secrets.token_urlsafe(32)

        # Store token (using verification code)
        from domain.account.models import VerificationCode

        # Create special code for reset via questions
        code_obj = VerificationCode.objects.create(
            user=user,
            code=reset_token[:6].upper(),  # Use part as code
            type="security",  # Special type
            purpose=VerificationPurpose.PASSWORD_RESET,
        )

        logger.info(f"Security questions verification successful for {user.identifier}")

        return SecurityQuestionsVerifyResult(
            success=True, reset_token=reset_token, expires_in=600  # 10 minutes
        )

    # =========================================================================
    # SECURITY SCORE
    # =========================================================================

    def get_security_summary(self, user: CustomUser) -> dict:
        """Return user's security summary."""
        return user.get_security_summary()

    def calculate_score(self, user: CustomUser) -> int:
        """Calculate security score."""
        return user.security_score

    # =========================================================================
    # UTILITIES
    # =========================================================================

    def _is_attempts_locked(self, user: CustomUser, ip_address: str) -> bool:
        """Check if attempts are locked."""
        lockout_minutes = self.config.get("LOGIN_LOCKOUT_MINUTES", 30)
        max_attempts = self.config.get("LOGIN_MAX_ATTEMPTS", 5)

        since = timezone.now() - timezone.timedelta(minutes=lockout_minutes)

        recent_failures = SecurityQuestionAttempt.objects.filter(
            user=user, success=False, created_at__gte=since
        ).count()

        return recent_failures >= max_attempts

    def _get_remaining_attempts(self, user: CustomUser) -> int:
        """Return remaining attempts."""
        lockout_minutes = self.config.get("LOGIN_LOCKOUT_MINUTES", 30)
        max_attempts = self.config.get("LOGIN_MAX_ATTEMPTS", 5)

        since = timezone.now() - timezone.timedelta(minutes=lockout_minutes)

        recent_failures = SecurityQuestionAttempt.objects.filter(
            user=user, success=False, created_at__gte=since
        ).count()

        return max(0, max_attempts - recent_failures)
