# domain/accounts/services/security.py

"""
Service de sécurité.
Gère: questions de sécurité, score de sécurité.
"""

import logging
import secrets
from typing import List, Optional
from dataclasses import dataclass
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from domain.accounts.models import CustomUser, SecurityQuestion, SecurityQuestionAttempt
from domain.accounts.constants import PREDEFINED_SECURITY_QUESTIONS
from domain.accounts.exceptions import (
    SecurityQuestionsRequiredError,
    SecurityAnswersInvalidError,
    SecurityMaxAttemptsError,
    ValidationError,
)

logger = logging.getLogger(__name__)


@dataclass
class SecurityQuestionsConfig:
    """Configuration des questions de sécurité."""

    predefined_questions: List[str]
    min_required: int
    max_allowed: int
    allow_custom: bool


@dataclass
class UserSecurityQuestions:
    """Questions de sécurité d'un utilisateur."""

    configured_count: int
    questions: List[dict]


@dataclass
class SecurityQuestionsSetupResult:
    """Résultat de la configuration des questions."""

    configured_count: int
    security_score: int
    security_level: str


@dataclass
class SecurityQuestionsVerifyResult:
    """Résultat de la vérification des réponses."""

    success: bool
    reset_token: Optional[str]
    expires_in: int


class SecurityService:
    """Service de gestion de la sécurité."""

    def __init__(self):
        self.config = getattr(settings, "ACCOUNTS_CONFIG", {})

    # =========================================================================
    # CONFIGURATION DES QUESTIONS
    # =========================================================================

    def get_questions_config(self) -> SecurityQuestionsConfig:
        """Retourne la configuration des questions de sécurité."""
        return SecurityQuestionsConfig(
            predefined_questions=PREDEFINED_SECURITY_QUESTIONS.copy(),
            min_required=self.config.get("MIN_SECURITY_QUESTIONS_FOR_RECOVERY", 2),
            max_allowed=self.config.get("MAX_SECURITY_QUESTIONS", 3),
            allow_custom=True,
        )

    def get_user_questions(self, user: CustomUser) -> UserSecurityQuestions:
        """Retourne les questions configurées par l'utilisateur."""
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
        Configure les questions de sécurité d'un utilisateur.

        Args:
            user: L'utilisateur
            questions: Liste de dicts avec 'question' et 'answer'

        Returns:
            SecurityQuestionsSetupResult

        Raises:
            ValidationError: Si données invalides
        """
        min_required = self.config.get("MIN_SECURITY_QUESTIONS_FOR_RECOVERY", 2)
        max_allowed = self.config.get("MAX_SECURITY_QUESTIONS", 3)

        # Validation
        if len(questions) < min_required:
            raise ValidationError(
                message=f"Au moins {min_required} questions sont requises",
                field_errors={
                    "questions": [f"Minimum {min_required} questions requises"]
                },
            )

        if len(questions) > max_allowed:
            raise ValidationError(
                message=f"Maximum {max_allowed} questions autorisées",
                field_errors={
                    "questions": [f"Maximum {max_allowed} questions autorisées"]
                },
            )

        # Valider chaque question
        for i, q in enumerate(questions):
            if not q.get("question") or len(q["question"].strip()) < 10:
                raise ValidationError(
                    message="La question doit contenir au moins 10 caractères",
                    field_errors={f"questions.{i}.question": ["Question trop courte"]},
                )

            if not q.get("answer") or len(q["answer"].strip()) < 2:
                raise ValidationError(
                    message="La réponse doit contenir au moins 2 caractères",
                    field_errors={f"questions.{i}.answer": ["Réponse trop courte"]},
                )

        # Supprimer les anciennes questions
        SecurityQuestion.objects.filter(user=user).delete()

        # Créer les nouvelles
        for i, q in enumerate(questions):
            SecurityQuestion.create_for_user(
                user=user,
                question=q["question"].strip(),
                answer=q["answer"].strip(),
                order=i + 1,
            )

        logger.info(
            f"Questions de sécurité configurées pour {user.identifier}: "
            f"{len(questions)} questions"
        )

        return SecurityQuestionsSetupResult(
            configured_count=len(questions),
            security_score=user.security_score,
            security_level=user.security_level,
        )

    # =========================================================================
    # VÉRIFICATION DES RÉPONSES
    # =========================================================================

    @transaction.atomic
    def verify_answers(
        self, identifier: str, answers: List[dict], ip_address: str = None
    ) -> SecurityQuestionsVerifyResult:
        """
        Vérifie les réponses aux questions de sécurité.

        Args:
            identifier: Email ou téléphone
            answers: Liste de dicts avec 'order' et 'answer'
            ip_address: Adresse IP du client

        Returns:
            SecurityQuestionsVerifyResult avec token de reset si succès

        Raises:
            SecurityQuestionsRequiredError: Si pas de questions configurées
            SecurityAnswersInvalidError: Si réponses incorrectes
            SecurityMaxAttemptsError: Si trop de tentatives
        """
        # Trouver l'utilisateur
        user = CustomUser.objects.get_by_identifier(identifier.strip())

        if not user:
            # Même message pour ne pas révéler l'existence du compte
            raise SecurityAnswersInvalidError()

        # Vérifier que des questions sont configurées
        user_questions = SecurityQuestion.objects.filter(user=user)
        if not user_questions.exists():
            raise SecurityQuestionsRequiredError()

        # Vérifier le rate limiting
        if self._is_attempts_locked(user, ip_address):
            raise SecurityMaxAttemptsError()

        # Vérifier les réponses
        min_correct = self.config.get("MIN_SECURITY_QUESTIONS_FOR_RECOVERY", 2)
        correct_count = 0

        for answer_data in answers:
            order = answer_data.get("order")
            answer = answer_data.get("answer", "")

            question = user_questions.filter(order=order).first()
            if question and question.check_answer(answer):
                correct_count += 1

        # Enregistrer la tentative
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

        # Succès - générer un token temporaire
        reset_token = secrets.token_urlsafe(32)

        # Stocker le token (on utilise le cache ou une table temporaire)
        # Pour simplifier, on stocke dans la session ou on crée un code de vérification spécial
        from domain.accounts.models import VerificationCode
        from domain.accounts.constants import VerificationPurpose

        # Créer un code spécial pour le reset via questions
        code_obj = VerificationCode.objects.create(
            user=user,
            code=reset_token[:6].upper(),  # Utiliser une partie comme code
            type="security",  # Type spécial
            purpose=VerificationPurpose.PASSWORD_RESET,
        )

        logger.info(f"Vérification questions réussie pour {user.identifier}")

        return SecurityQuestionsVerifyResult(
            success=True, reset_token=reset_token, expires_in=600  # 10 minutes
        )

    # =========================================================================
    # SCORE DE SÉCURITÉ
    # =========================================================================

    def get_security_summary(self, user: CustomUser) -> dict:
        """Retourne le résumé de sécurité d'un utilisateur."""
        return user.get_security_summary()

    def calculate_score(self, user: CustomUser) -> int:
        """Calcule le score de sécurité."""
        return user.security_score

    # =========================================================================
    # UTILITAIRES
    # =========================================================================

    def _is_attempts_locked(self, user: CustomUser, ip_address: str) -> bool:
        """Vérifie si les tentatives sont verrouillées."""
        lockout_minutes = self.config.get("LOGIN_LOCKOUT_MINUTES", 30)
        max_attempts = self.config.get("LOGIN_MAX_ATTEMPTS", 5)

        since = timezone.now() - timezone.timedelta(minutes=lockout_minutes)

        recent_failures = SecurityQuestionAttempt.objects.filter(
            user=user, success=False, created_at__gte=since
        ).count()

        return recent_failures >= max_attempts

    def _get_remaining_attempts(self, user: CustomUser) -> int:
        """Retourne le nombre de tentatives restantes."""
        lockout_minutes = self.config.get("LOGIN_LOCKOUT_MINUTES", 30)
        max_attempts = self.config.get("LOGIN_MAX_ATTEMPTS", 5)

        since = timezone.now() - timezone.timedelta(minutes=lockout_minutes)

        recent_failures = SecurityQuestionAttempt.objects.filter(
            user=user, success=False, created_at__gte=since
        ).count()

        return max(0, max_attempts - recent_failures)
