# apps/accounts/models/security.py

"""
Modèles liés aux questions de sécurité.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.hashers import make_password, check_password
from django.conf import settings

from ..constants import PREDEFINED_SECURITY_QUESTIONS


class SecurityQuestion(models.Model):
    """
    Question de sécurité pour la récupération de compte.

    L'utilisateur peut configurer jusqu'à 3 questions.
    Les réponses sont hachées pour la sécurité.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_questions",
        verbose_name=_("Utilisateur"),
    )

    question = models.CharField(
        verbose_name=_("Question"),
        max_length=255,
        help_text=_("La question de sécurité."),
    )

    answer_hash = models.CharField(
        verbose_name=_("Réponse (hachée)"),
        max_length=255,
        help_text=_("Réponse hachée pour la sécurité."),
    )

    order = models.PositiveSmallIntegerField(
        verbose_name=_("Ordre"),
        default=1,
        help_text=_("Ordre de la question (1, 2 ou 3)."),
    )

    created_at = models.DateTimeField(
        verbose_name=_("Date de création"), auto_now_add=True
    )

    updated_at = models.DateTimeField(
        verbose_name=_("Dernière modification"), auto_now=True
    )

    class Meta:
        verbose_name = _("Question de sécurité")
        verbose_name_plural = _("Questions de sécurité")
        ordering = ["user", "order"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "order"], name="unique_user_question_order"
            ),
            models.CheckConstraint(
                condition=models.Q(order__gte=1, order__lte=3),
                name="valid_question_order",
                violation_error_message=_("L'ordre doit être entre 1 et 3."),
            ),
        ]

    def __str__(self):
        return f"{self.user} - Question {self.order}"

    def set_answer(self, raw_answer: str) -> None:
        """
        Hache et stocke la réponse.

        La réponse est normalisée (lowercase, strip) avant hachage.
        """
        normalized = self._normalize_answer(raw_answer)
        self.answer_hash = make_password(normalized)

    def check_answer(self, raw_answer: str) -> bool:
        """
        Vérifie si la réponse est correcte.
        """
        normalized = self._normalize_answer(raw_answer)
        return check_password(normalized, self.answer_hash)

    @staticmethod
    def _normalize_answer(answer: str) -> str:
        """Normalise une réponse pour comparaison."""
        return answer.strip().lower()

    @classmethod
    def get_predefined_questions(cls) -> list[str]:
        """Retourne la liste des questions prédéfinies."""
        return PREDEFINED_SECURITY_QUESTIONS.copy()

    @classmethod
    def create_for_user(
        cls, user, question: str, answer: str, order: int
    ) -> "SecurityQuestion":
        """
        Crée une question de sécurité pour un utilisateur.

        Args:
            user: L'utilisateur
            question: La question
            answer: La réponse (sera hachée)
            order: L'ordre (1, 2 ou 3)

        Returns:
            Instance SecurityQuestion créée
        """
        instance = cls(user=user, question=question, order=order)
        instance.set_answer(answer)
        instance.save()
        return instance


class SecurityQuestionAttempt(models.Model):
    """
    Trace les tentatives de réponse aux questions de sécurité.
    Pour la protection contre les attaques brute-force.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="security_question_attempts",
        verbose_name=_("Utilisateur"),
    )

    ip_address = models.GenericIPAddressField(verbose_name=_("Adresse IP"), null=True)

    questions_answered = models.PositiveSmallIntegerField(
        verbose_name=_("Questions répondues"), default=0
    )

    correct_answers = models.PositiveSmallIntegerField(
        verbose_name=_("Réponses correctes"), default=0
    )

    success = models.BooleanField(verbose_name=_("Succès"), default=False)

    created_at = models.DateTimeField(verbose_name=_("Date"), auto_now_add=True)

    class Meta:
        verbose_name = _("Tentative questions sécurité")
        verbose_name_plural = _("Tentatives questions sécurité")
        ordering = ["-created_at"]

        indexes = [
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["ip_address", "created_at"]),
        ]
