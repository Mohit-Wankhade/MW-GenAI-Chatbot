from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
from uuid import uuid4

from jose import JWTError, jwt
from passlib.context import CryptContext

from config import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class TokenVerificationError(Exception):
    """Raised when JWT token verification fails."""


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def normalize_username(username: str) -> str:
    """
    Keeps usernames consistent across register/login/token validation.

    Example:
    ' Mohit ' -> 'mohit'
    """

    return username.strip().lower()


def hash_password(password: str) -> str:
    if not password:
        raise ValueError("Password cannot be empty.")

    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if not plain_password or not hashed_password:
        return False

    return pwd_context.verify(plain_password, hashed_password)


def validate_password_policy(password: str) -> None:
    """
    Basic production-friendly password policy.

    You can make this stricter later, but this is enough for a portfolio-grade app.
    """

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    if len(password) > 128:
        raise ValueError("Password must be less than 128 characters.")

    if password.strip() != password:
        raise ValueError("Password cannot start or end with spaces.")


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Creates a signed JWT access token.

    Required claim:
    - sub: username/user identifier

    Added claims:
    - exp: expiry
    - iat: issued at
    - jti: token id
    - type: access
    """

    to_encode = data.copy()

    expire = _utc_now() + (
        expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    to_encode.update(
        {
            "exp": expire,
            "iat": _utc_now(),
            "jti": str(uuid4()),
            "type": "access",
        }
    )

    return jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM,
    )


def verify_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT access token.

    Raises:
        TokenVerificationError
    """

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
        )

        if payload.get("type") != "access":
            raise TokenVerificationError("Invalid token type.")

        subject = payload.get("sub")

        if not subject or not isinstance(subject, str):
            raise TokenVerificationError("Missing token subject.")

        return payload

    except JWTError as exc:
        raise TokenVerificationError("Invalid token.") from exc