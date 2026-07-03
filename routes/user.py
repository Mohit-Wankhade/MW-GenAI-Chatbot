from fastapi import APIRouter, Depends
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import APIRouter, Depends, HTTPException, status

from db.mongo import users_collection
from auth.auth_handler import (
    hash_password,
    verify_password,
    create_access_token
)
from auth.auth_dependencies import get_current_user
from db.conversation_manager import (
    get_conversations,
    get_messages
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(request: RegisterRequest):

    existing_user = users_collection.find_one(
        {"username": request.username}
    )

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    users_collection.insert_one({
        "username": request.username,
        "password": hash_password(request.password)
    })

    return {
        "message": "User registered successfully"
    }
    
    
@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):

    user = users_collection.find_one({
        "username": form_data.username
    })

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    if not verify_password(
        form_data.password,
        user["password"]
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = create_access_token({
        "sub": form_data.username
    })

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@router.get("/conversations")
def conversations(

    current_user: str = Depends(get_current_user)

):

    return get_conversations(current_user)


@router.get("/conversation/{conversation_id}")
def conversation_messages(

    conversation_id: str,
    current_user: str = Depends(get_current_user)

):

    return get_messages(conversation_id)