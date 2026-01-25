# domain/accounts/tests/conftest.py

"""
Fixtures partagées pour les tests.
"""

import pytest
from django.core.cache import cache
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()


# =============================================================================
# FIXTURE POUR EFFACER LE CACHE AVANT CHAQUE TEST
# =============================================================================


@pytest.fixture(autouse=True)
def clear_cache():
    """Efface le cache avant chaque test (pour le throttling)."""
    cache.clear()
    yield
    cache.clear()


# =============================================================================
# USER FIXTURES
# =============================================================================


@pytest.fixture
def api_client():
    """Client API non authentifié."""
    return APIClient()


@pytest.fixture
def user_data():
    """Données de base pour créer un utilisateur."""
    return {
        "email": "test@example.com",
        "phone": "+224620000001",
        "password": "SecurePass123",
        "first_name": "Test",
        "last_name": "User",
    }


@pytest.fixture
def user(db, user_data):
    """Utilisateur de test non vérifié."""
    return User.objects.create_user(
        email=user_data["email"],
        phone=user_data["phone"],
        password=user_data["password"],
        first_name=user_data["first_name"],
        last_name=user_data["last_name"],
    )


@pytest.fixture
def verified_user(db, user):
    """Utilisateur de test vérifié."""
    user.email_verified = True
    user.phone_verified = True
    user.save()
    return user


@pytest.fixture
def user_with_email_only(db):
    """Utilisateur avec email uniquement."""
    return User.objects.create_user(
        email="emailonly@example.com",
        password="SecurePass123",
        first_name="Email",
        last_name="Only",
    )


@pytest.fixture
def user_with_phone_only(db):
    """Utilisateur avec téléphone uniquement."""
    return User.objects.create_user(
        phone="+224620000002",
        password="SecurePass123",
        first_name="Phone",
        last_name="Only",
    )


@pytest.fixture
def superuser(db):
    """Super utilisateur."""
    return User.objects.create_superuser(
        email="admin@example.com",
        password="AdminPass123",
        first_name="Admin",
        last_name="User",
    )


# =============================================================================
# AUTH FIXTURES
# =============================================================================


@pytest.fixture
def auth_tokens(user):
    """Tokens JWT pour un utilisateur."""
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


@pytest.fixture
def authenticated_client(api_client, auth_tokens):
    """Client API authentifié."""
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {auth_tokens['access']}")
    return api_client


@pytest.fixture
def verified_authenticated_client(api_client, verified_user):
    """Client API authentifié avec utilisateur vérifié."""
    refresh = RefreshToken.for_user(verified_user)
    api_client.credentials(HTTP_AUTHORIZATION=f"Bearer {str(refresh.access_token)}")
    return api_client


# =============================================================================
# SECURITY QUESTIONS FIXTURES
# =============================================================================


@pytest.fixture
def security_questions_data():
    """Données pour les questions de sécurité."""
    return {
        "questions": [
            {
                "question": "Quel est le nom de votre école primaire ?",
                "answer": "École Primaire de Matoto",
            },
            {"question": "Quel est le prénom de votre mère ?", "answer": "Mariama"},
            {
                "question": "Quel est votre plat préféré ?",
                "answer": "Riz sauce feuilles",
            },
        ]
    }


@pytest.fixture
def user_with_security_questions(verified_user, security_questions_data):
    """Utilisateur avec questions de sécurité configurées."""
    from domain.accounts.models import SecurityQuestion

    for i, q_data in enumerate(security_questions_data["questions"]):
        SecurityQuestion.create_for_user(
            user=verified_user,
            question=q_data["question"],
            answer=q_data["answer"],
            order=i + 1,
        )

    return verified_user


# =============================================================================
# VERIFICATION FIXTURES
# =============================================================================


@pytest.fixture
def verification_code(user):
    """Code de vérification pour un utilisateur."""
    from domain.accounts.models import VerificationCode
    from domain.accounts.constants import VerificationType, VerificationPurpose

    return VerificationCode.objects.create_code(
        user=user,
        verification_type=VerificationType.EMAIL,
        purpose=VerificationPurpose.ACCOUNT_VERIFICATION,
    )
