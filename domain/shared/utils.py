"""
Shared utility functions.

This module contains reusable helper functions.
"""

import re
import uuid
import unicodedata
from typing import Optional, List, Any


def get_constraint_name(
    model_name: str, constraint_type: str, *fields: str, suffix: Optional[str] = None
) -> str:
    """
    Generate a standardized constraint name.

    Args:
        model_name: Model name (snake_case)
        constraint_type: Constraint type ('uq', 'chk', 'idx')
        *fields: Concerned fields
        suffix: Optional suffix

    Returns:
        str: Formatted constraint name

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
    Truncate a string to a maximum length.

    Args:
        value: String to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        str: Truncated string

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
    Normalize a string (trim, unicode normalization).

    Args:
        value: String to normalize

    Returns:
        str: Normalized string
    """
    if not value:
        return ""

    # Trim
    value = value.strip()

    # Unicode normalization (NFC)
    value = unicodedata.normalize("NFC", value)

    # Remove multiple spaces
    value = re.sub(r"\s+", " ", value)

    return value


def generate_code(prefix: str = "", length: int = 8, uppercase: bool = True) -> str:
    """
    Generate a unique code.

    Args:
        prefix: Optional prefix
        length: Code length (without prefix)
        uppercase: If True, code in uppercase

    Returns:
        str: Generated unique code

    Example:
        >>> generate_code('USR', 6)
        'USR-A1B2C3'
    """
    # Generate random part based on UUID
    random_part = uuid.uuid4().hex[:length]

    if uppercase:
        random_part = random_part.upper()

    if prefix:
        return f"{prefix}-{random_part}"

    return random_part


def slugify(value: str, allow_unicode: bool = False) -> str:
    """
    Convert a string to a URL-friendly slug.

    Args:
        value: String to convert
        allow_unicode: If True, keep unicode characters

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
    Divide a list into chunks of size n.

    Args:
        lst: List to divide
        n: Chunk size

    Yields:
        List: Chunks of size n

    Example:
        >>> list(chunks([1, 2, 3, 4, 5], 2))
        [[1, 2], [3, 4], [5]]
    """
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def safe_int(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to int.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        int: Converted value or default
    """
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value: Any, default: float = 0.0) -> float:
    """
    Safely convert a value to float.

    Args:
        value: Value to convert
        default: Default value if conversion fails

    Returns:
        float: Converted value or default
    """
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def first_or_none(iterable):
    """
    Return the first element of an iterable or None.

    Args:
        iterable: Iterable

    Returns:
        First element or None
    """
    try:
        return next(iter(iterable))
    except StopIteration:
        return None


def coalesce(*args):
    """
    Return the first non-None argument.

    Args:
        *args: Arguments to check

    Returns:
        First non-None argument or None

    Example:
        >>> coalesce(None, None, "default")
        'default'
    """
    for arg in args:
        if arg is not None:
            return arg
    return None
