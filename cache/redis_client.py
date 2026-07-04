import redis
import json
import os
from utils.monitoring import (
    CACHE_HITS,
    CACHE_MISSES
)

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

def cache_response(query: str, response: str, ttl=3600):
    redis_client.setex(query, ttl, response)

def get_cached_response(query):

    data = redis_client.get(query)

    if data:
        CACHE_HITS.inc()
    else:
        CACHE_MISSES.inc()

    return data