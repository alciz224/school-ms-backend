# domain/accounts/tests/test_models.py

"""
Tests pour les models du module accounts.
"""

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

from domain.accounts.models import (
    SecurityQuestion,
    VerificationCode,
    PhoneHistory,
    LoginAttempt,
)
from domain.accounts.constants import VerificationType, VerificationPurpose

User = get_user_model()


# =============================================================================
# CUSTOM USER TESTS
# =============================================================================


@pytest.mark.django_db
class TestCustomUser:
    """Tests pour le model CustomUser."""

    def test_create_user_with_email(self):
        """Créer un utilisateur avec email."""
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123",
            first_name="Test",
            last_name="User",
        )

        assert user.email == "test@example.com"
        assert user.phone is None
        assert user.check_password("TestPass123")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_with_phone(self):
        """Créer un utilisateur avec téléphone."""
        user = User.objects.create_user(
            phone="+224620123456",
            password="TestPass123",
            first_name="Test",
            last_name="User",
        )

        assert user.phone == "+224620123456"
        assert user.email is None
        assert user.check_password("TestPass123")

    def test_create_user_with_email_and_phone(self):
        """Créer un utilisateur avec email et téléphone."""
        user = User.objects.create_user(
            email="test@example.com",
            phone="+224620123456",
            password="TestPass123",
            first_name="Test",
            last_name="User",
        )

        assert user.email == "test@example.com"
        assert user.phone == "+224620123456"

    def test_create_user_without_identifier_fails(self):
        """Échec si ni email ni téléphone."""
        with pytest.raises(ValidationError):
            User.objects.create_user(
                password="TestPass123",
                first_name="Test",
                last_name="User",
            )

    def test_create_superuser(self):
        """Créer un superutilisateur."""
        user = User.objects.create_superuser(
            email="admin@example.com",
            password="AdminPass123",
            first_name="Admin",
            last_name="User",
        )

        assert user.is_staff
        assert user.is_superuser
        assert user.email_verified  # Auto-vérifié

    def test_email_normalization(self):
        """L'email est normalisé en minuscules."""
        user = User.objects.create_user(
            email="TEST@EXAMPLE.COM",
            password="TestPass123",
            first_name="Test",
            last_name="User",
        )

        assert user.email == "test@example.com"

    def test_full_name_property(self, user):
        """Test de la propriété full_name."""
        assert user.full_name == "Test User"

    def test_is_verified_false_by_default(self, user):
        """L'utilisateur n'est pas vérifié par défaut."""
        assert not user.is_verified
        assert not user.email_verified
        assert not user.phone_verified

    def test_is_verified_with_email(self, user):
        """is_verified True si email vérifié."""
        user.email_verified = True
        user.save()

        assert user.is_verified

    def test_is_verified_with_phone(self, user):
        """is_verified True si téléphone vérifié."""
        user.phone_verified = True
        user.save()

        assert user.is_verified

    def test_masked_email(self, user):
        """Test du masquage de l'email."""
        assert user.masked_email is not None
        assert "@" in user.masked_email
        assert "*" in user.masked_email

    def test_masked_phone(self, user):
        """Test du masquage du téléphone."""
        assert user.masked_phone is not None
        assert "X" in user.masked_phone

    def test_security_score_initial(self, user):
        """Score de sécurité initial."""
        score = user.security_score
        assert score > 0
        assert score < 100

    def test_security_score_increases_with_verification(self, user):
        """Le score augmente avec la vérification."""
        initial_score = user.security_score

        user.email_verified = True
        user.save()

        assert user.security_score > initial_score

    def test_security_suggestions(self, user):
        """Suggestions de sécurité."""
        suggestions = user.security_suggestions

        assert isinstance(suggestions, list)
        assert len(suggestions) > 0

    def test_update_email(self, user):
        """Mise à jour de l'email."""
        old_email = user.email
        user.update_email("new@example.com")

        assert user.email == "new@example.com"
        assert user.email != old_email
        assert not user.email_verified  # Réinitialisé

    def test_update_phone(self, user):
        """Mise à jour du téléphone."""
        old_phone = user.phone
        user.update_phone("+224621000000")

        assert user.phone == "+224621000000"
        assert user.phone != old_phone
        assert not user.phone_verified  # Réinitialisé

    def test_phone_history_created_on_update(self, user):
        """Historique créé lors du changement de téléphone."""
        old_phone = user.phone
        user.update_phone("+224621000000")

        history = PhoneHistory.objects.filter(user=user, phone=old_phone)
        assert history.exists()

    def test_get_by_identifier_email(self, user):
        """Trouver un utilisateur par email."""
        found = User.objects.get_by_identifier(user.email)
        assert found == user

    def test_get_by_identifier_phone(self, user):
        """Trouver un utilisateur par téléphone."""
        found = User.objects.get_by_identifier(user.phone)
        assert found == user

    def test_get_by_identifier_not_found(self):
        """Retourne None si non trouvé."""
        found = User.objects.get_by_identifier("notfound@example.com")
        assert found is None


# =============================================================================
# SECURITY QUESTION TESTS
# =============================================================================


@pytest.mark.django_db
class TestSecurityQuestion:
    """Tests pour le model SecurityQuestion."""

    def test_create_security_question(self, user):
        """Créer une question de sécurité."""
        question = SecurityQuestion.create_for_user(
            user=user,
            question="Quel est le nom de votre école ?",
            answer="École Primaire",
            order=1,
        )

        assert question.user == user
        assert question.order == 1
        assert question.answer_hash != "École Primaire"  # Hashé

    def test_check_answer_correct(self, user):
        """Vérifier une réponse correcte."""
        question = SecurityQuestion.create_for_user(
            user=user, question="Test ?", answer="Réponse", order=1
        )

        assert question.check_answer("Réponse")
        assert question.check_answer("réponse")  # Case insensitive
        assert question.check_answer("  Réponse  ")  # Trimmed

    def test_check_answer_incorrect(self, user):
        """Vérifier une réponse incorrecte."""
        question = SecurityQuestion.create_for_user(
            user=user, question="Test ?", answer="Réponse", order=1
        )

        assert not question.check_answer("Mauvaise réponse")

    def test_max_three_questions_per_user(self, user):
        """Maximum 3 questions par utilisateur."""
        for i in range(3):
            SecurityQuestion.create_for_user(
                user=user,
                question=f"Question {i+1} ?",
                answer=f"Réponse {i+1}",
                order=i + 1,
            )

        assert user.security_questions.count() == 3

    def test_predefined_questions_available(self):
        """Les questions prédéfinies sont disponibles."""
        questions = SecurityQuestion.get_predefined_questions()

        assert isinstance(questions, list)
        assert len(questions) > 0


# =============================================================================
# VERIFICATION CODE TESTS
# =============================================================================


@pytest.mark.django_db
class TestVerificationCode:
    """Tests pour le model VerificationCode."""

    def test_create_verification_code(self, user):
        """Créer un code de vérification."""
        code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )

        assert code.user == user
        assert len(code.code) == 6
        assert code.code.isdigit()
        assert not code.is_used
        assert not code.is_expired

    def test_code_expires(self, user):
        """Le code expire après le délai."""
        from django.utils import timezone
        from datetime import timedelta

        code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )

        # Simuler l'expiration
        code.expires_at = timezone.now() - timedelta(minutes=1)
        code.save()

        assert code.is_expired

    def test_verify_correct_code(self, user):
        """Vérifier un code correct."""
        code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )

        result = code.verify(code.code)

        assert result is True
        assert code.is_used

    def test_verify_incorrect_code(self, user):
        """Vérifier un code incorrect."""
        code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )

        result = code.verify("000000")

        assert result is False
        assert not code.is_used
        assert code.attempts == 1

    def test_max_attempts_reached(self, user):
        """Maximum de tentatives atteint."""
        code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )

        # Épuiser les tentatives
        for _ in range(3):
            code.verify("000000")

        assert code.max_attempts_reached

        # Même le bon code ne marche plus
        result = code.verify(code.code)
        assert result is False

    def test_old_codes_invalidated(self, user):
        """Les anciens codes sont invalidés."""
        code1 = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )

        code2 = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )

        code1.refresh_from_db()

        assert code1.is_used  # Invalidé
        assert not code2.is_used  # Actif


# =============================================================================
# LOGIN ATTEMPT TESTS
# =============================================================================


@pytest.mark.django_db
class TestLoginAttempt:
    """Tests pour le model LoginAttempt."""

    def test_record_successful_login(self, user):
        """Enregistrer une connexion réussie."""
        attempt = LoginAttempt.record(
            identifier=user.email,
            ip_address="192.168.1.1",
            user=user,
            success=True,
            user_agent="Mozilla/5.0",
        )

        assert attempt.success is True
        assert attempt.user == user

    def test_record_failed_login(self, user):
        """Enregistrer une connexion échouée."""
        attempt = LoginAttempt.record(
            identifier=user.email,
            ip_address="192.168.1.1",
            user=user,
            success=False,
            failure_reason="invalid_password",
            user_agent="Mozilla/5.0",
        )

        assert attempt.success is False
        assert attempt.failure_reason == "invalid_password"

    def test_get_recent_failures(self, user):
        """Compter les échecs récents."""
        for _ in range(3):
            LoginAttempt.record(
                identifier=user.email,
                ip_address="192.168.1.1",
                success=False,
                failure_reason="invalid_password",
            )

        failures = LoginAttempt.get_recent_failures(identifier=user.email)
        assert failures == 3

    def test_is_locked_out(self, user):
        """Détection du verrouillage."""
        # Créer 5 échecs
        for _ in range(5):
            LoginAttempt.record(
                identifier=user.email,
                ip_address="192.168.1.1",
                success=False,
                failure_reason="invalid_password",
            )

        is_locked = LoginAttempt.is_locked_out(identifier=user.email)
        assert is_locked is True
