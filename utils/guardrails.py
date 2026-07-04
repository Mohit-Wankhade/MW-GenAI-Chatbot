import re
from typing import Optional

from better_profanity import profanity


MAX_QUERY_LENGTH = 6000
MIN_QUERY_LENGTH = 1

CONTROL_CHAR_PATTERN = re.compile(r"[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]")
REPEATED_CHAR_PATTERN = re.compile(r"(.)\1{80,}")


try:
    profanity.load_censor_words()
except Exception:
    # better_profanity usually works without explicit load,
    # so this should not break app startup.
    pass


def normalize_user_text(text: Optional[str]) -> str:
    """
    Normalizes user input while preserving meaningful formatting.
    """

    if text is None:
        return ""

    cleaned = str(text).replace("\x00", " ")
    cleaned = CONTROL_CHAR_PATTERN.sub(" ", cleaned)
    cleaned = cleaned.strip()

    return cleaned


def validate_input(text: Optional[str]) -> bool:
    """
    Basic input validation for chat queries.

    Kept as bool-returning function for compatibility with chat_service.py.
    """

    cleaned = normalize_user_text(text)

    if len(cleaned) < MIN_QUERY_LENGTH:
        return False

    if len(cleaned) > MAX_QUERY_LENGTH:
        return False

    if REPEATED_CHAR_PATTERN.search(cleaned):
        return False

    return True


def get_input_validation_error(text: Optional[str]) -> Optional[str]:
    """
    Optional helper for future routes/services when you want a specific error message.
    """

    cleaned = normalize_user_text(text)

    if len(cleaned) < MIN_QUERY_LENGTH:
        return "Input cannot be empty."

    if len(cleaned) > MAX_QUERY_LENGTH:
        return f"Input is too long. Maximum allowed length is {MAX_QUERY_LENGTH} characters."

    if REPEATED_CHAR_PATTERN.search(cleaned):
        return "Input contains excessive repeated characters."

    return None


def contains_profanity(text: Optional[str]) -> bool:
    cleaned = normalize_user_text(text)

    if not cleaned:
        return False

    try:
        return profanity.contains_profanity(cleaned)

    except Exception:
        return False


def sanitize_for_log(text: Optional[str], max_length: int = 300) -> str:
    """
    Prevents huge user inputs from polluting logs.
    """

    cleaned = normalize_user_text(text)

    if len(cleaned) > max_length:
        return cleaned[:max_length].rstrip() + "..."

    return cleaned