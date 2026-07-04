from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, ConfigDict, Field

from auth.auth_dependencies import get_current_user
from db.conversation_manager import (
    create_conversation,
    delete_conversation,
    get_conversations,
    get_messages,
    rename_conversation,
)


router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
)


class RenameRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(
        ...,
        min_length=1,
        max_length=80,
        description="New title for the conversation.",
    )


@router.post(
    "/new",
    status_code=status.HTTP_201_CREATED,
)
def new_chat(current_user: str = Depends(get_current_user)):
    conversation_id = create_conversation(
        user=current_user,
        title="New Chat",
    )

    return {
        "conversation_id": conversation_id,
        "title": "New Chat",
    }


@router.get("")
@router.get("/")
def list_conversations(current_user: str = Depends(get_current_user)):
    return get_conversations(current_user)


@router.get("/{conversation_id}/messages")
def get_conversation_messages(
    conversation_id: str,
    current_user: str = Depends(get_current_user),
):
    return get_messages(
        conversation_id=conversation_id,
        user=current_user,
    )


@router.put("/{conversation_id}")
def rename_chat(
    conversation_id: str,
    request: RenameRequest,
    current_user: str = Depends(get_current_user),
):
    rename_conversation(
        conversation_id=conversation_id,
        title=request.title,
        user=current_user,
    )

    return {
        "message": "Conversation renamed successfully.",
    }


@router.delete("/{conversation_id}")
def remove_conversation(
    conversation_id: str,
    current_user: str = Depends(get_current_user),
):
    delete_conversation(
        conversation_id=conversation_id,
        user=current_user,
    )

    return {
        "message": "Conversation deleted successfully.",
    }