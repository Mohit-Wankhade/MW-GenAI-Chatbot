from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status

from db.mongo import conversations_collection, messages_collection


VALID_MESSAGE_ROLES = {"user", "assistant", "system"}


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_object_id(value: str) -> ObjectId:
    try:
        return ObjectId(value)

    except (InvalidId, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conversation id.",
        )


def _serialize_datetime(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()

    return value


def _clean_title(title: str) -> str:
    cleaned = " ".join(title.strip().replace("\n", " ").split())

    if not cleaned:
        cleaned = "New Chat"

    if len(cleaned) > 60:
        cleaned = cleaned[:60].rstrip() + "..."

    return cleaned


def _generate_title_from_message(content: str) -> str:
    title = " ".join(content.strip().replace("\n", " ").split())

    if not title:
        return "New Chat"

    if len(title) > 45:
        title = title[:45].rstrip() + "..."

    return title


def _get_conversation_or_404(
    conversation_id: str,
    user: Optional[str] = None,
) -> Dict[str, Any]:
    object_id = _to_object_id(conversation_id)

    query = {"_id": object_id}

    if user is not None:
        query["user"] = user

    conversation = conversations_collection.find_one(query)

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found.",
        )

    return conversation


def create_conversation(
    user: str,
    title: str = "New Chat",
) -> str:
    now = _utc_now()

    result = conversations_collection.insert_one(
        {
            "user": user,
            "title": _clean_title(title),
            "created_at": now,
            "updated_at": now,
            "message_count": 0,
        }
    )

    return str(result.inserted_id)


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    sources: Optional[List[Dict[str, Any]]] = None,
) -> str:
    """
    Saves one message inside a conversation.

    This remains compatible with your existing chat_service.py because it only
    requires conversation_id, role, content, and optional sources.
    """

    if role not in VALID_MESSAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid message role. Allowed roles: {sorted(VALID_MESSAGE_ROLES)}",
        )

    clean_content = content.strip() if isinstance(content, str) else ""

    if not clean_content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Message content cannot be empty.",
        )

    conversation = _get_conversation_or_404(conversation_id)
    conversation_object_id = conversation["_id"]

    now = _utc_now()

    result = messages_collection.insert_one(
        {
            "conversation_id": conversation_object_id,
            "role": role,
            "content": clean_content,
            "sources": sources or [],
            "timestamp": now,
        }
    )

    update_data: Dict[str, Any] = {
        "updated_at": now,
    }

    if conversation.get("title") == "New Chat" and role == "user":
        update_data["title"] = _generate_title_from_message(clean_content)

    conversations_collection.update_one(
        {"_id": conversation_object_id},
        {
            "$set": update_data,
            "$inc": {"message_count": 1},
        },
    )

    return str(result.inserted_id)


def get_conversations(user: str) -> List[Dict[str, Any]]:
    conversations = conversations_collection.find(
        {"user": user}
    ).sort("updated_at", -1)

    result = []

    for convo in conversations:
        result.append(
            {
                "id": str(convo["_id"]),
                "title": convo.get("title", "New Chat"),
                "created_at": _serialize_datetime(convo.get("created_at")),
                "updated_at": _serialize_datetime(convo.get("updated_at")),
                "message_count": convo.get("message_count", 0),
            }
        )

    return result


def get_messages_for_llm(
    conversation_id: str,
    user: Optional[str] = None,
    limit: int = 12,
) -> List[Dict[str, str]]:
    """
    Returns recent messages in LLM-friendly format.

    Keeps only role + content to avoid leaking DB metadata into prompts.
    """

    conversation = _get_conversation_or_404(
        conversation_id=conversation_id,
        user=user,
    )

    safe_limit = max(1, min(limit, 30))

    recent_messages = (
        messages_collection.find(
            {
                "conversation_id": conversation["_id"],
                "role": {"$in": ["user", "assistant", "system"]},
            }
        )
        .sort("timestamp", -1)
        .limit(safe_limit)
    )

    messages = list(recent_messages)
    messages.reverse()

    return [
        {
            "role": message.get("role", "user"),
            "content": message.get("content", ""),
        }
        for message in messages
    ]


def get_messages(
    conversation_id: str,
    user: Optional[str] = None,
) -> List[Dict[str, Any]]:
    conversation = _get_conversation_or_404(
        conversation_id=conversation_id,
        user=user,
    )

    messages = messages_collection.find(
        {
            "conversation_id": conversation["_id"],
        }
    ).sort("timestamp", 1)

    result = []

    for message in messages:
        result.append(
            {
                "id": str(message["_id"]),
                "role": message.get("role"),
                "content": message.get("content"),
                "sources": message.get("sources", []),
                "timestamp": _serialize_datetime(message.get("timestamp")),
            }
        )

    return result


def delete_conversation(
    conversation_id: str,
    user: Optional[str] = None,
) -> bool:
    conversation = _get_conversation_or_404(
        conversation_id=conversation_id,
        user=user,
    )

    messages_collection.delete_many(
        {
            "conversation_id": conversation["_id"],
        }
    )

    conversations_collection.delete_one(
        {
            "_id": conversation["_id"],
        }
    )

    return True


def rename_conversation(
    conversation_id: str,
    title: str,
    user: Optional[str] = None,
) -> bool:
    conversation = _get_conversation_or_404(
        conversation_id=conversation_id,
        user=user,
    )

    conversations_collection.update_one(
        {
            "_id": conversation["_id"],
        },
        {
            "$set": {
                "title": _clean_title(title),
                "updated_at": _utc_now(),
            }
        },
    )

    return True