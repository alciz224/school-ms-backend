"""
Fonctions utilitaires partagées.

Ce module contient des fonctions helper réutilisables.
"""

import re
import uuid
import unicodedata
from typing import Optional, List, Any


def get_constraint_name(
    model_name: str, constraint_type: str, *fields: str, suffix: Optional[str] = None
) -> str:
    """
    Génère un nom de contrainte standardisé.

    Args:
        model_name: Nom du modèle (snake_case)
        constraint_type: Type de contrainte ('uq', 'chk', 'idx')
        *fields: Champs concernés
        suffix: Suffixe optionnel

    Returns:
        str: Nom de contrainte formaté

    Example:
        >>> get_constraint_name('school_year', 'uq', 'school', 'academic_year')
        'uq_school_year_school_academic_year'
        >>> get_constraint_name('school_year', 'chk', suffix='active_not_deleted')
        'chk_school_year_active_not_deleted'
    """
    parts = [constraint_type, model_name]

    if fields:
        parts.extend(fields)

    if suffix:
        parts.append(suffix)

    return "_".join(parts)


def truncate_string(value: str, max_length: int, suffix: str = "...") -> str:
    """
    Tronque une chaîne à une longueur maximale.

    Args:
        value: Chaîne à tronquer
        max_length: Longueur maximale
        suffix: Suffixe à ajouter si tronqué

    Returns:
        str: Chaîne tronquée

    Example:
        >>> truncate_string("Hello World", 8)
        'Hello...'
    """
    if not value:
        return ""

    if len(value) <= max_length:
        return value

    return value[: max_length - len(suffix)] + suffix


def normalize_string(value: str) -> str:
    """
    Normalise une chaîne (trim, normalisation unicode).

    Args:
        value: Chaîne à normaliser

    Returns:
        str: Chaîne normalisée
    """
    if not value:
        return ""

    # Trim
    value = value.strip()

    # Normalisation unicode (NFC)
    value = unicodedata.normalize("NFC", value)

    # Supprimer les espaces multiples
    value = re.sub(r"\s+", " ", value)

    return value


def generate_code(prefix: str = "", length: int = 8, uppercase: bool = True) -> str:
    """
    Génère un code unique.

    Args:
        prefix: Préfixe optionnel
        length: Longueur du code (sans préfixe)
        uppercase: Si True, code en majuscules

    Returns:
        str: Code unique généré

    Example:
        >>> generate_code('USR', 6)
        'USR-A1B2C3'
    """
    # Générer une partie aléatoire basée sur UUID
    random_part = uuid.uuid4().hex[:length]

    if uppercase:
        random_part = random_part.upper()

    if prefix:
        return f"{prefix}-{random_part}"

    return random_part


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convertit une chaîne en slug URL-friendly.

    Args:
        value: Chaîne à convertir
        allow_unicode: Si True, garde les caractères unicode

    Returns:
        str: Slug

    Example:
        >>> slugify("Hello World!")
        'hello-world'
    """
    if not value:
        return ""

    value = str(value)

    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = unicodedata.normalize("NFKD", value)
        value = value.encode("ascii", "ignore").decode("ascii")

    value = re.sub(r"[^\w\s-]", "", value.lower())
    value = re.sub(r"[-\s]+", "-", value).strip("-_")

    return value


def chunks(lst: List[Any], n: int):
    """
    Divise une liste en chunks de taille n.

    Args:
        lst: Liste à diviser
        n: Taille des chunks

    Yields:
        List: Chunks de taille n

    Example:
        >>> list(chunks([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def safe_int(value: Any, default: int = 0) -> int:
    """
    Convertit une valeur en int de manière sécurisée.

    Args:
        value: Valeur à convertir
        default: Valeur par défaut si conversion échoue

    Returns:
        int: Valeur convertie ou default
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Convertit une valeur en float de manière sécurisée.

    Args:
        value: Valeur à convertir
        default: Valeur par défaut si conversion échoue

    Returns:
        float: Valeur convertie ou default
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def first_or_none(iterable):
    """
    Retourne le premier élément d'un itérable ou None.

    Args:
        iterable: Itérable

    Returns:
        Premier élément ou None
    """
    try:
        return next(iter(iterable))
    except StopIteration:
        return None


def coalesce(*args):
    """
    Retourne le premier argument non-None.

    Args:
        *args: Arguments à vérifier

    Returns:
        Premier argument non-None ou None

    Example:
        >>> coalesce(None, None, "default")
        'default'
    """
    for arg in args:
        if arg is not None:
            return arg
    return None
