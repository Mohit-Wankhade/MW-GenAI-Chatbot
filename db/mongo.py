from pymongo import MongoClient
from utils.logger import logger 
from config import MONGO_URL

client= MongoClient(MONGO_URL,serverSelectionTimeoutMS=5000)
try:
    client.admin.command('ping')
    logger.info("MongoDB connection successful")
except Exception as e:
    logger.error("MongoDB connection failed:", e)  

db= client["chatbot_db"]
collection= db["history"]
users_collection= db["users"]
conversations_collection = db["conversations"]
messages_collection = db["messages"]

from datetime import datetime, timezone
def save_chat(query, response):
    
    result= collection.insert_one({
        "query": query,
        "response": response,
        "timestamp": datetime.now(timezone.utc)
    })
    logger.info("Inserted chat id: %s", result.inserted_id)
    
def get_recent_chats(limit=10):
    chats= collection.find().sort("timestamp", -1).limit(limit)
    return list(chats)