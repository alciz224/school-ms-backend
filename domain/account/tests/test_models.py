"""
Unit tests for account models.

Focus: Core model behavior, validation, and business logic.
"""

import pytest
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.utils import timezone

from domain.account.models import SecurityQuestion, VerificationCode
from domain.account.constants import VerificationType, VerificationPurpose

User = get_user_model()


@pytest.mark.django_db
class TestCustomUser:
    """Tests for CustomUser model."""

    def test_create_user_with_email(self):
        """User can be created with email only."""
        user = User.objects.create_user(
            email="test@example.com",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "test@example.com"
        assert user.phone is None
        assert user.check_password("TestPass123!")
        assert user.is_active
        assert not user.is_staff

    def test_create_user_with_phone(self):
        """User can be created with phone only."""
        user = User.objects.create_user(
            phone="+224620123456",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
        )
        assert user.phone == "+224620123456"
        assert user.email is None

    def test_create_user_without_identifier_fails(self):
        """User creation fails without email or phone."""
        with pytest.raises(ValidationError):
            User.objects.create_user(
                password="TestPass123!",
                first_name="Test",
                last_name="User",
            )

    def test_email_normalized(self):
        """Email domain is lowercased."""
        user = User.objects.create_user(
            email="Test@EXAMPLE.COM",
            password="TestPass123!",
            first_name="Test",
            last_name="User",
        )
        assert user.email == "Test@example.com"

    def test_duplicate_email_fails(self, user):
        """Duplicate email raises error."""
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(
                email=user.email,
                password="OtherPass123!",
                first_name="Dup",
                last_name="User",
            )

    def test_duplicate_phone_fails(self, user):
        """Duplicate phone raises error."""
        with pytest.raises(Exception):  # IntegrityError
            User.objects.create_user(
                phone=user.phone,
                password="OtherPass123!",
                first_name="Dup",
                last_name="User",
            )

    # Properties
    def test_full_name(self, user):
        """full_name returns first + last name."""
        assert user.full_name == "Test User"

    def test_identifier_returns_email_first(self, user):
        """identifier returns email when available."""
        assert user.identifier == user.email

    def test_identifier_returns_phone_if_no_email(self):
        """identifier returns phone when no email."""
        user = User.objects.create_user(
            phone="+224620000001",
            password="TestPass123!",
            first_name="Phone",
            last_name="User",
        )
        assert user.identifier == "+224620000001"

    def test_masked_email(self, user):
        """masked_email hides middle characters."""
        # testuser@example.com -> t******r@example.com
        assert user.masked_email is not None
        assert "@" in user.masked_email
        assert user.masked_email != user.email

    def test_masked_phone(self, user):
        """masked_phone hides middle digits."""
        assert user.masked_phone is not None
        assert user.masked_phone != user.phone

    def test_is_verified_false_by_default(self, user):
        """New user is not verified."""
        assert not user.is_verified
        assert not user.email_verified
        assert not user.phone_verified

    def test_is_verified_true_after_email_verify(self, user):
        """User is verified after email verification."""
        user.verify_email()
        assert user.is_verified
        assert user.email_verified
        assert user.email_verified_at is not None

    def test_is_verified_true_after_phone_verify(self, user):
        """User is verified after phone verification."""
        user.verify_phone()
        assert user.is_verified
        assert user.phone_verified

    # Security score
    def test_security_score_initial(self, user):
        """New user has base security score."""
        score = user.security_score
        assert 0 <= score <= 100

    def test_security_score_increases_with_verification(self, user):
        """Score increases when verified."""
        initial_score = user.security_score
        user.verify_email()
        assert user.security_score > initial_score

    def test_security_level(self, user):
        """security_level is low/medium/high based on score."""
        assert user.security_level in ("low", "medium", "high")

    def test_security_suggestions(self, user):
        """security_suggestions returns improvement tips."""
        suggestions = user.security_suggestions
        assert isinstance(suggestions, list)


@pytest.mark.django_db
class TestSecurityQuestion:
    """Tests for SecurityQuestion model."""

    def test_create_question(self, user):
        """Security question can be created."""
        sq = SecurityQuestion.create_for_user(
            user=user,
            question="What is your favorite color?",
            answer="Blue",
            order=1,
        )
        assert sq.user == user
        assert sq.question == "What is your favorite color?"
        assert sq.order == 1

    def test_answer_is_hashed(self, user):
        """Answer is stored as hash, not plaintext."""
        sq = SecurityQuestion.create_for_user(
            user=user,
            question="What is your pet's name?",
            answer="Fluffy",
            order=1,
        )
        assert sq.answer_hash != "Fluffy"
        assert sq.answer_hash != "fluffy"

    def test_check_answer_correct(self, user):
        """check_answer returns True for correct answer."""
        sq = SecurityQuestion.create_for_user(
            user=user,
            question="Favorite movie?",
            answer="Inception",
            order=1,
        )
        assert sq.check_answer("Inception")
        assert sq.check_answer("inception")  # Case insensitive
        assert sq.check_answer("  INCEPTION  ")  # Trimmed

    def test_check_answer_incorrect(self, user):
        """check_answer returns False for wrong answer."""
        sq = SecurityQuestion.create_for_user(
            user=user,
            question="Favorite movie?",
            answer="Inception",
            order=1,
        )
        assert not sq.check_answer("Matrix")

    def test_order_constraint(self, user):
        """Order must be between 1 and 3."""
        SecurityQuestion.create_for_user(user=user, question="Q1?Q1?Q1?Q1?", answer="A1", order=1)
        SecurityQuestion.create_for_user(user=user, question="Q2?Q2?Q2?Q2?", answer="A2", order=2)
        SecurityQuestion.create_for_user(user=user, question="Q3?Q3?Q3?Q3?", answer="A3", order=3)
        
        # Can't have duplicate order for same user
        with pytest.raises(Exception):
            SecurityQuestion.create_for_user(user=user, question="Q4?Q4?Q4?Q4?", answer="A4", order=1)

    def test_user_security_questions_count(self, user):
        """User can track security question count."""
        assert user.security_questions_count == 0
        SecurityQuestion.create_for_user(user=user, question="What city?What city?", answer="Paris", order=1)
        user.refresh_from_db()
        assert user.security_questions_count == 1


@pytest.mark.django_db
class TestVerificationCode:
    """Tests for VerificationCode model."""

    def test_create_code(self, user):
        """Verification code can be created."""
        code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )
        assert code.user == user
        assert code.code is not None
        assert len(code.code) == 6
        assert code.code.isdigit()

    def test_code_is_valid_when_fresh(self, user):
        """Fresh code is valid."""
        code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )
        assert not code.is_expired
        assert not code.is_used
        assert code.remaining_attempts > 0

    def test_verify_correct_code(self, user):
        """Correct code verifies successfully."""
        code_obj = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )
        raw_code = code_obj.code
        
        # verify() is on the instance
        result = code_obj.verify(raw_code)
        assert result is True
        assert code_obj.is_used

    def test_verify_wrong_code(self, user):
        """Wrong code fails verification."""
        code_obj = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )
        
        result = code_obj.verify("000000")
        assert result is False
        assert not code_obj.is_used
        assert code_obj.attempts == 1

    def test_creating_new_code_invalidates_old(self, user):
        """Creating new code invalidates previous one."""
        old_code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )
        old_code_value = old_code.code
        
        # Create new code - this invalidates old one
        new_code = VerificationCode.objects.create_code(
            user=user,
            verification_type=VerificationType.EMAIL,
            purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
        )
        
        # Old code should be marked as used (invalidated)
        old_code.refresh_from_db()
        assert old_code.is_used is True
        
        # New code should work
        assert new_code.verify(new_code.code) is True
