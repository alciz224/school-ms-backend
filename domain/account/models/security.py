"""
Security question related models.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings

from ..constants import PREDEFINED_SECURITY_QUESTIONS


class SecurityQuestion(models.Model):
    """
    Security question for account recovery.

    User can configure up to 3 questions.
    Answers are hashed for security.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_questions",
        verbose_name=_("User"),
    )

    question = models.CharField(
        verbose_name=_("Question"),
        max_length=255,
        help_text=_("The security question."),
    )

    answer_hash = models.CharField(
        verbose_name=_("Answer (hashed)"),
        max_length=255,
        help_text=_("Hashed answer for security."),
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_("Order"),
        default=1,
        help_text=_("Question order (1, 2, or 3)."),
    )

    created_at = models.DateTimeField(
        verbose_name=_("Created at"), auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Last modified"), auto_now=True
    )

    class Meta:
        verbose_name = _("Security question")
        verbose_name_plural = _("Security questions")
        ordering = ["user", "order"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "order"], name="unique_user_question_order"
            ),
            models.CheckConstraint(
                condition=models.Q(order__gte=1, order__lte=3),
                name="valid_question_order",
                violation_error_message=_("Order must be between 1 and 3."),
            ),
        ]

    def __str__(self):
        return f"{self.user} - Question {self.order}"

    def set_answer(self, raw_answer: str) -> None:
        """
        Hash and store the answer.

        The answer is normalized (lowercase, strip) before hashing.
        """
        normalized = self._normalize_answer(raw_answer)
        self.answer_hash = make_password(normalized)

    def check_answer(self, raw_answer: str) -> bool:
        """
        Check if the answer is correct.
        """
        normalized = self._normalize_answer(raw_answer)
        return check_password(normalized, self.answer_hash)

    @staticmethod
    def _normalize_answer(answer: str) -> str:
        """Normalize an answer for comparison."""
        return answer.strip().lower()

    @classmethod
    def get_predefined_questions(cls) -> list[str]:
        """Return the list of predefined questions."""
        return PREDEFINED_SECURITY_QUESTIONS.copy()

    @classmethod
    def create_for_user(
        cls, user, question: str, answer: str, order: int
    ) -> "SecurityQuestion":
        """
        Create a security question for a user.

        Args:
            user: The user
            question: The question
            answer: The answer (will be hashed)
            order: The order (1, 2, or 3)

        Returns:
            Created SecurityQuestion instance
        """
        instance = cls(user=user, question=question, order=order)
        instance.set_answer(answer)
        instance.save()
        return instance


class SecurityQuestionAttempt(models.Model):
    """
    Track security question answer attempts.
    For brute-force protection.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_question_attempts",
        verbose_name=_("User"),
    )

    ip_address = models.GenericIPAddressField(verbose_name=_("IP address"), null=True)

    questions_answered = models.PositiveSmallIntegerField(
        verbose_name=_("Questions answered"), default=0
    )

    correct_answers = models.PositiveSmallIntegerField(
        verbose_name=_("Correct answers"), default=0
    )

    success = models.BooleanField(verbose_name=_("Success"), default=False)

    created_at = models.DateTimeField(verbose_name=_("Date"), auto_now_add=True)

    class Meta:
        verbose_name = _("Security question attempt")
        verbose_name_plural = _("Security question attempts")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["ip_address", "created_at"]),
        ]
