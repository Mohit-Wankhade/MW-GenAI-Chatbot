from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, ConfigDict, Field, field_validator
from pymongo.errors import DuplicateKeyError

from auth.auth_dependencies import get_current_user
from auth.auth_handler import (
    create_access_token,
    hash_password,
    normalize_username,
    validate_password_policy,
    verify_password,
)
from db.conversation_manager import get_conversations, get_messages
from db.mongo import users_collection


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username for login.",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password must be at least 8 characters.",
    )
    full_name: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional display name.",
    )

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        username = normalize_username(value)

        if not username.replace("_", "").replace(".", "").isalnum():
            raise ValueError(
                "Username can only contain letters, numbers, dots, and underscores."
            )

        return username


class UserResponse(BaseModel):
    username: str
    full_name: Optional[str] = None
    created_at: Optional[datetime] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str


def _sanitize_user(user: dict) -> dict:
    return {
        "username": user.get("username"),
        "full_name": user.get("full_name"),
        "created_at": user.get("created_at"),
    }


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(request: RegisterRequest):
    username = normalize_username(request.username)

    try:
        validate_password_policy(request.password)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        )

    existing_user = users_collection.find_one({"username": username})

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    now = datetime.now(timezone.utc)

    user_document = {
        "username": username,
        "password": hash_password(request.password),
        "full_name": request.full_name.strip() if request.full_name else None,
        "created_at": now,
        "updated_at": now,
        "last_login_at": None,
        "is_active": True,
    }

    try:
        users_collection.insert_one(user_document)

    except DuplicateKeyError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    return _sanitize_user(user_document)


@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = normalize_username(form_data.username)

    user = users_collection.find_one({"username": username})

    invalid_credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not user:
        raise invalid_credentials_exception

    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled.",
        )

    if not verify_password(form_data.password, user.get("password", "")):
        raise invalid_credentials_exception

    users_collection.update_one(
        {"_id": user["_id"]},
        {
            "$set": {
                "last_login_at": datetime.now(timezone.utc),
                "updated_at": datetime.now(timezone.utc),
            }
        },
    )

    token = create_access_token({"sub": username})

    return {
        "access_token": token,
        "token_type": "bearer",
        "username": username,
    }


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(current_user: str = Depends(get_current_user)):
    user = users_collection.find_one({"username": current_user})

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    return _sanitize_user(user)


@router.get("/conversations")
def conversations(current_user: str = Depends(get_current_user)):
    """
    Kept here for backward compatibility with your existing frontend.

    Recommended future route:
    /conversations from routes/conversation.py
    """

    return get_conversations(current_user)


@router.get("/conversation/{conversation_id}")
def conversation_messages(
    conversation_id: str,
    current_user: str = Depends(get_current_user),
):
    """
    Securely returns messages only if the conversation belongs to current user.
    """

    return get_messages(
        conversation_id=conversation_id,
        user=current_user,
    )