import redis
import json
import os

redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "redis"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=int(os.getenv("REDIS_DB", 0)),
    decode_responses=True
)

def get_cache(key):
    data = redis_client.get(key)
    if data:
        return json.loads(data)
    return None

def set_cache(key, value, expire=3600):
    redis_client.setex(key, expire, json.dumps(value))

def get_cached_response(query: str):
    return redis_client.get(query)

def cache_response(query: str, response: str, ttl=3600):
    redis_client.setex(query, ttl, response)