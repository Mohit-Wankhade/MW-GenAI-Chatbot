from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from auth.auth_handler import TokenVerificationError, verify_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    """
    Validates the JWT access token and returns the authenticated username.

    This dependency should be used on every protected route.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = verify_token(token)
        username = payload.get("sub")

        if not username or not isinstance(username, str):
            raise credentials_exception

        return username

    except TokenVerificationError:
        raise credentials_exception


def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """
    Optional advanced dependency.

    Use this when a route needs the full JWT payload instead of only username.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        return verify_token(token)

    except TokenVerificationError:
        raise credentials_exception