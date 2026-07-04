from datetime import datetime, timezone
from typing import Any, Dict, List

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from config import (
    MONGO_CHAT_COLLECTION,
    MONGO_DB_NAME,
    MONGO_URL,
    MONGO_USER_COLLECTION,
)
from utils.logger import logger


DEFAULT_LOCAL_MONGO_URL = "mongodb://localhost:27017"


def _create_client() -> MongoClient:
    mongo_url = MONGO_URL or DEFAULT_LOCAL_MONGO_URL

    client = MongoClient(
        mongo_url,
        serverSelectionTimeoutMS=5000,
        connectTimeoutMS=5000,
        socketTimeoutMS=10000,
        appname="genai-chatbot",
        retryWrites=True,
    )

    try:
        client.admin.command("ping")
        logger.info("MongoDB connection successful.")

    except Exception as exc:
        logger.error("MongoDB connection failed: %s", exc)

    return client


client: MongoClient = _create_client()

db: Database = client[MONGO_DB_NAME]

# Backward-compatible collection names
collection: Collection = db[MONGO_CHAT_COLLECTION]
users_collection: Collection = db[MONGO_USER_COLLECTION]

# Main conversation collections
conversations_collection: Collection = db["conversations"]
messages_collection: Collection = db["messages"]


def create_indexes() -> None:
    """
    Creates useful indexes for performance and data integrity.

    Safe to call multiple times.
    """

    try:
        users_collection.create_index(
            [("username", ASCENDING)],
            unique=True,
            name="unique_username_idx",
        )

        conversations_collection.create_index(
            [("user", ASCENDING), ("updated_at", DESCENDING)],
            name="user_updated_at_idx",
        )

        conversations_collection.create_index(
            [("created_at", DESCENDING)],
            name="conversation_created_at_idx",
        )

        messages_collection.create_index(
            [("conversation_id", ASCENDING), ("timestamp", ASCENDING)],
            name="conversation_messages_idx",
        )

        collection.create_index(
            [("timestamp", DESCENDING)],
            name="history_timestamp_idx",
        )

        logger.info("MongoDB indexes ensured successfully.")

    except PyMongoError as exc:
        logger.error("MongoDB index creation failed: %s", exc)


create_indexes()


def serialize_mongo_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """
    Converts MongoDB ObjectId and datetime fields into JSON-friendly strings.
    """

    serialized = {}

    for key, value in document.items():
        if key == "_id":
            serialized["id"] = str(value)
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value

    return serialized


def save_chat(query: str, response: str) -> str:
    """
    Legacy helper kept for compatibility.

    Newer code should prefer db.conversation_manager.save_message().
    """

    result = collection.insert_one(
        {
            "query": query,
            "response": response,
            "timestamp": datetime.now(timezone.utc),
        }
    )

    logger.info("Inserted legacy chat id: %s", result.inserted_id)

    return str(result.inserted_id)


def get_recent_chats(limit: int = 10) -> List[Dict[str, Any]]:
    """
    Legacy helper kept for compatibility.
    """

    safe_limit = max(1, min(limit, 50))

    chats = (
        collection.find()
        .sort("timestamp", DESCENDING)
        .limit(safe_limit)
    )

    return [serialize_mongo_document(chat) for chat in chats]