# domain/accounts/tests/test_services.py

"""
Tests pour les services du module accounts.
"""

import pytest
from django.contrib.auth import get_user_model

from domain.accounts.services import (
    AuthService,
    VerificationService,
    PasswordService,
    SecurityService,
)
from domain.accounts.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    PhoneAlreadyExistsError,
    WeakPasswordError,
    VerificationCodeInvalidError,
    InvalidCurrentPasswordError,
)

User = get_user_model()


# =============================================================================
# AUTH SERVICE TESTS
# =============================================================================


@pytest.mark.django_db
class TestAuthService:
    """Tests pour AuthService."""

    def setup_method(self):
        self.service = AuthService()

    def test_register_with_email(self):
        """Inscription avec email."""
        result = self.service.register(
            email="new@example.com",
            password="SecurePass123",
            first_name="New",
            last_name="User",
        )

        assert result.user is not None
        assert result.user.email == "new@example.com"
        assert result.tokens.access is not None
        assert result.tokens.refresh is not None
        assert result.requires_verification is True

    def test_register_with_phone(self):
        """Inscription avec téléphone."""
        result = self.service.register(
            phone="+224620000003",
            password="SecurePass123",
            first_name="Phone",
            last_name="User",
        )

        assert result.user.phone == "+224620000003"

    def test_register_with_email_and_phone(self):
        """Inscription avec email et téléphone."""
        result = self.service.register(
            email="both@example.com",
            phone="+224620000004",
            password="SecurePass123",
            first_name="Both",
            last_name="User",
        )

        assert result.user.email == "both@example.com"
        assert result.user.phone == "+224620000004"

    def test_register_duplicate_email_fails(self, user):
        """Échec si email déjà utilisé."""
        with pytest.raises(EmailAlreadyExistsError):
            self.service.register(
                email=user.email,
                password="SecurePass123",
                first_name="Dup",
                last_name="User",
            )

    def test_register_duplicate_phone_fails(self, user):
        """Échec si téléphone déjà utilisé."""
        with pytest.raises(PhoneAlreadyExistsError):
            self.service.register(
                phone=user.phone,
                password="SecurePass123",
                first_name="Dup",
                last_name="User",
            )

    def test_register_weak_password_fails(self):
        """Échec si mot de passe faible."""
        with pytest.raises(WeakPasswordError):
            self.service.register(
                email="weak@example.com",
                password="123",
                first_name="Weak",
                last_name="Pass",
            )

    def test_login_with_email(self, user, user_data):
        """Connexion avec email."""
        result = self.service.login(
            identifier=user.email,
            password=user_data["password"],
            ip_address="127.0.0.1",
        )

        assert result.user == user
        assert result.tokens.access is not None

    def test_login_with_phone(self, user, user_data):
        """Connexion avec téléphone."""
        result = self.service.login(
            identifier=user.phone,
            password=user_data["password"],
            ip_address="127.0.0.1",
        )

        assert result.user == user

    def test_login_invalid_password(self, user):
        """Échec avec mauvais mot de passe."""
        with pytest.raises(InvalidCredentialsError):
            self.service.login(
                identifier=user.email, password="WrongPassword", ip_address="127.0.0.1"
            )

    def test_login_invalid_identifier(self):
        """Échec avec identifiant inexistant."""
        with pytest.raises(InvalidCredentialsError):
            self.service.login(
                identifier="notfound@example.com",
                password="SomePassword",
                ip_address="127.0.0.1",
            )

    def test_logout(self, auth_tokens):
        """Déconnexion."""
        result = self.service.logout(auth_tokens["refresh"])
        assert result is True


# =============================================================================
# VERIFICATION SERVICE TESTS
# =============================================================================


@pytest.mark.django_db
class TestVerificationService:
    """Tests pour VerificationService."""

    def setup_method(self):
        self.service = VerificationService()

    def test_send_code_email(self, user):
        """Envoyer un code par email."""
        result = self.service.send_code(user, "email")

        assert result.sent_to == user.email
        assert result.expires_in > 0

    def test_send_code_phone(self, user):
        """Envoyer un code par téléphone."""
        result = self.service.send_code(user, "phone")

        assert result.sent_to == user.phone

    def test_verify_code_success(self, user, verification_code):
        """Vérifier un code valide."""
        result = self.service.verify_code(
            user=user, code=verification_code.code, verification_type="email"
        )

        assert result.is_fully_verified is True

        user.refresh_from_db()
        assert user.email_verified is True

    def test_verify_code_invalid(self, user, verification_code):
        """Échec avec code invalide."""
        with pytest.raises(VerificationCodeInvalidError):
            self.service.verify_code(
                user=user, code="000000", verification_type="email"
            )

    def test_get_verification_status(self, user):
        """Récupérer le statut de vérification."""
        status = self.service.get_verification_status(user)

        assert "is_verified" in status
        assert "email" in status
        assert "phone" in status


# =============================================================================
# PASSWORD SERVICE TESTS
# =============================================================================


@pytest.mark.django_db
class TestPasswordService:
    """Tests pour PasswordService."""

    def setup_method(self):
        self.service = PasswordService()

    def test_request_reset(self, user):
        """Demander une réinitialisation."""
        result = self.service.request_reset(user.email)

        assert result.expires_in > 0
        assert result.next_step == "check_email_or_phone"

    def test_request_reset_unknown_user(self):
        """Demande avec utilisateur inconnu (pas d'erreur)."""
        result = self.service.request_reset("unknown@example.com")

        # Même réponse pour éviter l'énumération
        assert result.expires_in > 0

    def test_change_password(self, user, user_data):
        """Changer le mot de passe."""
        result = self.service.change_password(
            user=user,
            current_password=user_data["password"],
            new_password="NewSecurePass456",
        )

        assert result.success is True
        assert result.access_token is not None

        # Vérifier que le nouveau mot de passe fonctionne
        user.refresh_from_db()
        assert user.check_password("NewSecurePass456")

    def test_change_password_wrong_current(self, user):
        """Échec avec mauvais mot de passe actuel."""
        with pytest.raises(InvalidCurrentPasswordError):
            self.service.change_password(
                user=user,
                current_password="WrongPassword",
                new_password="NewSecurePass456",
            )


# =============================================================================
# SECURITY SERVICE TESTS
# =============================================================================


@pytest.mark.django_db
class TestSecurityService:
    """Tests pour SecurityService."""

    def setup_method(self):
        self.service = SecurityService()

    def test_get_questions_config(self):
        """Récupérer la configuration des questions."""
        config = self.service.get_questions_config()

        assert len(config.predefined_questions) > 0
        assert config.min_required == 2
        assert config.max_allowed == 3

    def test_setup_questions(self, verified_user, security_questions_data):
        """Configurer les questions de sécurité."""
        result = self.service.setup_questions(
            user=verified_user, questions=security_questions_data["questions"]
        )

        assert result.configured_count == 3
        assert result.security_score > 0

    def test_get_user_questions(self, user_with_security_questions):
        """Récupérer les questions d'un utilisateur."""
        result = self.service.get_user_questions(user_with_security_questions)

        assert result.configured_count == 3
        assert len(result.questions) == 3

    def test_get_security_summary(self, verified_user):
        """Récupérer le résumé de sécurité."""
        summary = self.service.get_security_summary(verified_user)

        assert "score" in summary
        assert "level" in summary
        assert "suggestions" in summary
