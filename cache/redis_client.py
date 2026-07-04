import json
from typing import Any, Optional

import redis
from redis.exceptions import RedisError

from config import REDIS_CACHE_TTL_SECONDS, REDIS_DB, REDIS_HOST, REDIS_PASSWORD, REDIS_PORT
from utils.logger import logger
from utils.monitoring import CACHE_HITS, CACHE_MISSES


def _create_redis_client() -> redis.Redis:
    return redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=REDIS_DB,
        password=REDIS_PASSWORD or None,
        decode_responses=True,
        socket_connect_timeout=3,
        socket_timeout=3,
        retry_on_timeout=True,
        health_check_interval=30,
    )


redis_client = _create_redis_client()


def is_redis_available() -> bool:
    try:
        redis_client.ping()
        return True

    except RedisError as exc:
        logger.warning("Redis unavailable: %s", exc)
        return False


def get_cache(key: str) -> Optional[Any]:
    """
    Generic JSON cache getter.

    Returns Python objects for values saved through set_cache().
    """

    if not key:
        return None

    try:
        data = redis_client.get(key)

        if data is None:
            CACHE_MISSES.inc()
            return None

        CACHE_HITS.inc()

        try:
            return json.loads(data)

        except json.JSONDecodeError:
            logger.warning("Redis value is not valid JSON for key=%s", key)
            return data

    except RedisError as exc:
        CACHE_MISSES.inc()
        logger.warning("Redis get failed for key=%s: %s", key, exc)
        return None


def set_cache(
    key: str,
    value: Any,
    expire: int = REDIS_CACHE_TTL_SECONDS,
) -> bool:
    """
    Generic JSON cache setter.
    """

    if not key:
        return False

    try:
        redis_client.setex(
            name=key,
            time=max(1, int(expire)),
            value=json.dumps(value, ensure_ascii=False, default=str),
        )
        return True

    except RedisError as exc:
        logger.warning("Redis set failed for key=%s: %s", key, exc)
        return False


def get_cached_response(key: str) -> Optional[str]:
    """
    Chat response cache getter.

    Used by services.chat_service.
    """

    if not key:
        return None

    try:
        data = redis_client.get(key)

        if data:
            CACHE_HITS.inc()
            return str(data)

        CACHE_MISSES.inc()
        return None

    except RedisError as exc:
        CACHE_MISSES.inc()
        logger.warning("Redis chat cache get failed for key=%s: %s", key, exc)
        return None


def cache_response(
    key: str,
    response: str,
    ttl: int = REDIS_CACHE_TTL_SECONDS,
) -> bool:
    """
    Chat response cache setter.

    Redis failures should never break the chatbot response flow.
    """

    if not key or not response:
        return False

    try:
        redis_client.setex(
            name=key,
            time=max(1, int(ttl)),
            value=response,
        )
        return True

    except RedisError as exc:
        logger.warning("Redis chat cache set failed for key=%s: %s", key, exc)
        return False


def delete_cache(key: str) -> bool:
    if not key:
        return False

    try:
        redis_client.delete(key)
        return True

    except RedisError as exc:
        logger.warning("Redis delete failed for key=%s: %s", key, exc)
        return False


def clear_cache_by_prefix(prefix: str) -> int:
    """
    Deletes cache keys matching a prefix.

    Useful later when you want to invalidate chat/RAG cache after reindexing.
    """

    if not prefix:
        return 0

    deleted = 0

    try:
        cursor = 0
        pattern = f"{prefix}*"

        while True:
            cursor, keys = redis_client.scan(
                cursor=cursor,
                match=pattern,
                count=100,
            )

            if keys:
                deleted += redis_client.delete(*keys)

            if cursor == 0:
                break

        return deleted

    except RedisError as exc:
        logger.warning("Redis prefix clear failed for prefix=%s: %s", prefix, exc)
        return deleted