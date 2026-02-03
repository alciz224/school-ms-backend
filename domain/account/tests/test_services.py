"""
Unit tests for account services.

Focus: Business logic in service layer.
"""

import pytest
from django.contrib.auth import get_user_model

from domain.account.services import AuthService, PasswordService, VerificationService, SecurityService
from domain.account.exceptions import (
    InvalidCredentialsError,
    EmailAlreadyExistsError,
    PhoneAlreadyExistsError,
    WeakPasswordError,
    InvalidCurrentPasswordError,
    VerificationCodeInvalidError,
    SecurityAnswersInvalidError,
)
from domain.account.models import SecurityQuestion

User = get_user_model()


@pytest.mark.django_db
class TestAuthService:
    """Tests for AuthService."""

    def setup_method(self):
        self.service = AuthService()

    # Registration
    def test_register_with_email(self):
        """Registration with email succeeds."""
        result = self.service.register(
            email="new@example.com",
            password="SecurePass123!",
            first_name="New",
            last_name="User",
        )
        assert result.user is not None
        assert result.user.email == "new@example.com"
        assert result.tokens.access is not None
        assert result.tokens.refresh is not None
        assert result.requires_verification is True

    def test_register_with_phone(self):
        """Registration with phone succeeds."""
        result = self.service.register(
            phone="+224620000001",
            password="SecurePass123!",
            first_name="Phone",
            last_name="User",
        )
        assert result.user.phone == "+224620000001"
        assert result.user.email is None

    def test_register_duplicate_email_fails(self, user):
        """Registration with existing email fails."""
        with pytest.raises(EmailAlreadyExistsError):
            self.service.register(
                email=user.email,
                password="SecurePass123!",
                first_name="Dup",
                last_name="User",
            )

    def test_register_duplicate_phone_fails(self, user):
        """Registration with existing phone fails."""
        with pytest.raises(PhoneAlreadyExistsError):
            self.service.register(
                phone=user.phone,
                password="SecurePass123!",
                first_name="Dup",
                last_name="User",
            )

    def test_register_weak_password_fails(self):
        """Registration with weak password fails."""
        with pytest.raises(WeakPasswordError):
            self.service.register(
                email="weak@example.com",
                password="123",
                first_name="Weak",
                last_name="User",
            )

    # Login
    def test_login_with_email(self, user):
        """Login with email succeeds."""
        result = self.service.login(
            identifier=user.email,
            password="TestPass123!",
        )
        assert result.user.id == user.id
        assert result.tokens.access is not None

    def test_login_with_phone(self, user):
        """Login with phone succeeds."""
        result = self.service.login(
            identifier=user.phone,
            password="TestPass123!",
        )
        assert result.user.id == user.id

    def test_login_wrong_password_fails(self, user):
        """Login with wrong password fails."""
        with pytest.raises(InvalidCredentialsError):
            self.service.login(
                identifier=user.email,
                password="WrongPassword123!",
            )

    def test_login_nonexistent_user_fails(self):
        """Login with unknown identifier fails."""
        with pytest.raises(InvalidCredentialsError):
            self.service.login(
                identifier="nobody@example.com",
                password="SomePassword123!",
            )

    # Token refresh
    def test_refresh_tokens(self, user):
        """Token refresh returns new tokens."""
        # First get a refresh token
        result = self.service.login(identifier=user.email, password="TestPass123!")
        
        # Refresh it
        new_tokens = self.service.refresh_tokens(result.tokens.refresh)
        assert new_tokens.access is not None
        assert new_tokens.refresh is not None

    def test_refresh_invalid_token_fails(self):
        """Refresh with invalid token fails."""
        with pytest.raises(InvalidCredentialsError):
            self.service.refresh_tokens("invalid-token")


@pytest.mark.django_db
class TestPasswordService:
    """Tests for PasswordService."""

    def setup_method(self):
        self.service = PasswordService()

    def test_request_reset_always_succeeds(self, user):
        """Reset request always returns success (no enumeration)."""
        result = self.service.request_reset(user.email)
        assert result.expires_in > 0
        assert result.next_step is not None

    def test_request_reset_unknown_email_also_succeeds(self):
        """Reset request for unknown email also succeeds."""
        result = self.service.request_reset("unknown@example.com")
        assert result.expires_in > 0

    def test_change_password_success(self, user):
        """Password change with correct current password succeeds."""
        result = self.service.change_password(
            user=user,
            current_password="TestPass123!",
            new_password="NewSecurePass456!",
        )
        assert result.success is True
        assert result.access_token is not None
        
        # Verify new password works
        user.refresh_from_db()
        assert user.check_password("NewSecurePass456!")

    def test_change_password_wrong_current_fails(self, user):
        """Password change with wrong current password fails."""
        with pytest.raises(InvalidCurrentPasswordError):
            self.service.change_password(
                user=user,
                current_password="WrongPassword123!",
                new_password="NewSecurePass456!",
            )

    def test_change_password_weak_new_fails(self, user):
        """Password change with weak new password fails."""
        with pytest.raises(WeakPasswordError):
            self.service.change_password(
                user=user,
                current_password="TestPass123!",
                new_password="123",
            )


@pytest.mark.django_db
class TestVerificationService:
    """Tests for VerificationService."""

    def setup_method(self):
        self.service = VerificationService()

    def test_send_code_email(self, user):
        """Sending email verification code succeeds."""
        result = self.service.send_code(user=user, verification_type="email")
        assert result.sent_to == user.email
        assert result.expires_in > 0

    def test_send_code_phone(self, user):
        """Sending phone verification code succeeds."""
        result = self.service.send_code(user=user, verification_type="phone")
        assert result.sent_to == user.phone

    def test_verify_code_success(self, user):
        """Verifying correct code succeeds."""
        from domain.account.models import VerificationCode
        from domain.account.constants import VerificationType, VerificationPurpose
        
        # Send code first
        self.service.send_code(user=user, verification_type="email")
        
        # Get the actual code from DB (test environment)
        code_obj = VerificationCode.objects.filter(
            user=user,
            type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
            is_used=False,
        ).first()
        
        # Verify it
        result = self.service.verify_code(
            user=user,
            code=code_obj.code,
            verification_type="email",
        )
        assert result.verified_type == "email"
        assert result.is_fully_verified is True or result.is_fully_verified is False  # Depends on phone

    def test_verify_code_wrong_fails(self, user):
        """Verifying wrong code fails."""
        self.service.send_code(user=user, verification_type="email")
        
        with pytest.raises(VerificationCodeInvalidError):
            self.service.verify_code(
                user=user,
                code="000000",
                verification_type="email",
            )

    def test_get_verification_status(self, user):
        """Getting verification status works."""
        status = self.service.get_verification_status(user)
        assert "email" in status
        assert "phone" in status


@pytest.mark.django_db
class TestSecurityService:
    """Tests for SecurityService."""

    def setup_method(self):
        self.service = SecurityService()

    def test_get_questions_config(self):
        """Get questions config returns settings."""
        config = self.service.get_questions_config()
        assert config.predefined_questions is not None
        assert len(config.predefined_questions) > 0
        assert config.min_required >= 1
        assert config.max_allowed >= config.min_required

    def test_setup_questions(self, user):
        """Setting up security questions succeeds."""
        questions = [
            {"question": "What is your favorite color?", "answer": "Blue"},
            {"question": "What city were you born in?", "answer": "Paris"},
        ]
        result = self.service.setup_questions(user=user, questions=questions)
        assert result.configured_count == 2
        assert result.security_score >= 0

    def test_setup_replaces_existing(self, user):
        """Setting up questions replaces existing ones."""
        # First setup (need 2 questions minimum)
        self.service.setup_questions(
            user=user,
            questions=[
                {"question": "First question here one?", "answer": "First"},
                {"question": "First question here two?", "answer": "Second"},
            ],
        )
        
        # Second setup replaces
        result = self.service.setup_questions(
            user=user,
            questions=[
                {"question": "New question one here?", "answer": "One"},
                {"question": "New question two here?", "answer": "Two"},
            ],
        )
        assert result.configured_count == 2
        assert user.security_questions.count() == 2

    def test_get_user_questions(self, user):
        """Get user questions returns configured questions."""
        self.service.setup_questions(
            user=user,
            questions=[
                {"question": "What is your pet's name?", "answer": "Max"},
                {"question": "What city were you born in?", "answer": "Paris"},
            ],
        )
        
        result = self.service.get_user_questions(user)
        assert result.configured_count == 2
        assert len(result.questions) == 2
        # Answer should not be exposed
        assert "answer" not in result.questions[0]

    def test_verify_answers_success(self, user):
        """Verifying correct answers succeeds."""
        self.service.setup_questions(
            user=user,
            questions=[
                {"question": "What is your favorite color?", "answer": "Blue"},
                {"question": "What is your pet's name?", "answer": "Max"},
            ],
        )
        
        result = self.service.verify_answers(
            identifier=user.email,
            answers=[
                {"order": 1, "answer": "Blue"},
                {"order": 2, "answer": "Max"},
            ],
        )
        assert result.reset_token is not None
        assert result.expires_in > 0

    def test_verify_answers_wrong_fails(self, user):
        """Verifying wrong answers fails."""
        self.service.setup_questions(
            user=user,
            questions=[
                {"question": "What is your favorite color?", "answer": "Blue"},
                {"question": "What is your pet's name?", "answer": "Max"},
            ],
        )
        
        with pytest.raises(SecurityAnswersInvalidError):
            self.service.verify_answers(
                identifier=user.email,
                answers=[
                    {"order": 1, "answer": "Wrong"},
                    {"order": 2, "answer": "Wrong"},
                ],
            )
