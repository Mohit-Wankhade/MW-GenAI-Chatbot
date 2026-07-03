from datetime import datetime, timezone
from bson import ObjectId

from db.mongo import (
    conversations_collection,
    messages_collection
)


def create_conversation(user: str, title: str):

    result = conversations_collection.insert_one({

        "user": user,
        "title": title,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc)

    })

    return str(result.inserted_id)


def save_message(
    conversation_id: str,
    role: str,
    content: str,
    sources=None
):

    messages_collection.insert_one({

        "conversation_id": ObjectId(conversation_id),
        "role": role,
        "content": content,
        "sources": sources or [],
        "timestamp": datetime.now(timezone.utc)

    })

    conversation = conversations_collection.find_one(
        {"_id": ObjectId(conversation_id)}
    )

    if (
        conversation
        and conversation.get("title") == "New Chat"
        and role == "user"
    ):

        title = content.strip()

        # Remove newlines
        title = title.replace("\n", " ")

        # Collapse multiple spaces
        title = " ".join(title.split())

        # Limit title length
        if len(title) > 45:
            title = title[:45].rstrip() + "..."

        conversations_collection.update_one(
            {"_id": ObjectId(conversation_id)},
            {
                "$set": {
                    "title": title
                }
            }
        )

    conversations_collection.update_one(

        {"_id": ObjectId(conversation_id)},

        {
            "$set": {
                "updated_at": datetime.now(timezone.utc)
            }
        }

    )


def get_conversations(user: str):

    conversations = conversations_collection.find(

        {"user": user}

    ).sort(

        "updated_at",
        -1

    )

    result = []

    for convo in conversations:

        result.append({

            "id": str(convo["_id"]),

            "title": convo["title"]

        })

    return result
def get_messages_for_llm(conversation_id: str):

    messages = messages_collection.find(
        {
            "conversation_id": ObjectId(conversation_id)
        }
    ).sort("timestamp", 1)

    result = []

    for message in messages:

        result.append({

            "role": message["role"],
            "content": message["content"]

        })

    return result

def get_messages(conversation_id: str):

    messages = messages_collection.find(
        {
            "conversation_id": ObjectId(conversation_id)
        }
    ).sort("timestamp", 1)

    result = []

    for message in messages:

        result.append({

            "role": message["role"],
            "content": message["content"],
            "sources": message.get("sources", [])

        })

    return result

def delete_conversation(conversation_id: str):

    messages_collection.delete_many({

        "conversation_id": ObjectId(conversation_id)

    })

    conversations_collection.delete_one({

        "_id": ObjectId(conversation_id)

    })

    return True

def rename_conversation(conversation_id: str, title: str):

    conversations_collection.update_one(
        {
            "_id": ObjectId(conversation_id)
        },
        {
            "$set": {
                "title": title,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

    return True