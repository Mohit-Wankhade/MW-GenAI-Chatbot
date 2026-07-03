from fastapi import APIRouter, Depends

from auth.auth_dependencies import get_current_user
from pydantic import BaseModel

from db.conversation_manager import (
    create_conversation,
    get_conversations,
    get_messages,
    delete_conversation,
    rename_conversation
)


router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"]
)
class RenameRequest(BaseModel):
    title: str

@router.put("/{conversation_id}")
def rename_chat(
    conversation_id: str,
    request: RenameRequest,
    current_user: str = Depends(get_current_user)
):

    rename_conversation(
        conversation_id,
        request.title
    )

    return {
        "message": "Conversation renamed."
    }
    
    
@router.post("/new")
def new_chat(
    current_user: str = Depends(get_current_user)
):

    conversation_id = create_conversation(
        current_user,
        "New Chat"
    )

    return {

        "conversation_id": conversation_id,

        "title": "New Chat"

    }
    
@router.delete("/{conversation_id}")
def remove_conversation(
    conversation_id: str,
    current_user: str = Depends(get_current_user)
):

    delete_conversation(conversation_id)

    return {

        "message": "Conversation deleted."

    }