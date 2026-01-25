# apps/accounts/validators.py

"""
Validateurs personnalisés pour les champs du modèle User.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
import phonenumbers
from phonenumbers import NumberParseException


def validate_phone_number(value: str) -> str:
    """
    Valide et normalise un numéro de téléphone.

    Args:
        value: Numéro de téléphone à valider

    Returns:
        Numéro normalisé au format E.164 (+224620123456)

    Raises:
        ValidationError: Si le numéro est invalide
    """
    if not value:
        return value

    # Nettoyer le numéro
    cleaned = re.sub(r"[\s\-\.\(\)]", "", value)

    # Région par défaut (Guinée)
    default_region = getattr(settings, "ACCOUNTS_CONFIG", {}).get(
        "DEFAULT_PHONE_REGION", "GN"
    )

    try:
        # Parser le numéro
        parsed = phonenumbers.parse(cleaned, default_region)

        # Vérifier la validité
        if not phonenumbers.is_valid_number(parsed):
            raise ValidationError(
                _("Ce numéro de téléphone n'est pas valide."), code="invalid_phone"
            )

        # Retourner au format E.164
        return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)

    except NumberParseException as e:
        raise ValidationError(
            _("Format de numéro de téléphone invalide: %(error)s"),
            code="invalid_phone_format",
            params={"error": str(e)},
        )


def validate_guinea_phone(value: str) -> str:
    """
    Valide spécifiquement un numéro guinéen.
    Accepte les formats: 620123456, +224620123456, 00224620123456
    """
    normalized = validate_phone_number(value)

    if normalized and not normalized.startswith("+224"):
        raise ValidationError(
            _("Seuls les numéros guinéens (+224) sont acceptés."),
            code="non_guinea_phone",
        )

    return normalized


def validate_password_strength(password: str) -> None:
    """
    Valide la force du mot de passe.

    Règles:
        - Minimum 8 caractères
        - Au moins une majuscule
        - Au moins une minuscule
        - Au moins un chiffre
    """
    if len(password) < 8:
        raise ValidationError(
            _("Le mot de passe doit contenir au moins 8 caractères."),
            code="password_too_short",
        )

    if not re.search(r"[A-Z]", password):
        raise ValidationError(
            _("Le mot de passe doit contenir au moins une majuscule."),
            code="password_no_upper",
        )

    if not re.search(r"[a-z]", password):
        raise ValidationError(
            _("Le mot de passe doit contenir au moins une minuscule."),
            code="password_no_lower",
        )

    if not re.search(r"[0-9]", password):
        raise ValidationError(
            _("Le mot de passe doit contenir au moins un chiffre."),
            code="password_no_digit",
        )


def check_password_strength(password: str) -> dict:
    """
    Évalue la force du mot de passe sans lever d'exception.

    Returns:
        dict avec 'score' (0-100) et 'issues' (liste de problèmes)
    """
    score = 0
    issues = []

    # Longueur
    if len(password) >= 8:
        score += 25
    else:
        issues.append("Minimum 8 caractères requis")

    if len(password) >= 12:
        score += 10

    # Complexité
    if re.search(r"[A-Z]", password):
        score += 20
    else:
        issues.append("Ajoutez une majuscule")

    if re.search(r"[a-z]", password):
        score += 20
    else:
        issues.append("Ajoutez une minuscule")

    if re.search(r"[0-9]", password):
        score += 15
    else:
        issues.append("Ajoutez un chiffre")

    if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        score += 10

    return {
        "score": min(score, 100),
        "is_strong": score >= 70 and len(issues) == 0,
        "issues": issues,
    }
