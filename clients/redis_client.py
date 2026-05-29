import logging
import redis.asyncio as aioredis
from config import settings

logger = logging.getLogger(__name__)

_redis: aioredis.Redis | None = None

THREAD_KEY_PREFIX = "thread:"


async def init_redis() -> None:
    global _redis
    _redis = aioredis.from_url(settings.REDIS_URL, decode_responses=True)


async def close_redis() -> None:
    global _redis
    if _redis is not None:
        await _redis.aclose()
        _redis = None


def _get_redis() -> aioredis.Redis:
    if _redis is None:
        raise RuntimeError("Redis client not initialized")
    return _redis


async def get_thread_id(phone_number: str) -> str | None:
    try:
        thread_id = await _get_redis().get(f"{THREAD_KEY_PREFIX}{phone_number}")
        return str(thread_id) if thread_id is not None else None
    except Exception:
        logger.exception("Failed to get thread_id from Redis for %s", phone_number)
        return None


async def set_thread_id(phone_number: str, thread_id: str) -> None:
    try:
        await _get_redis().set(
            f"{THREAD_KEY_PREFIX}{phone_number}",
            thread_id,
            ex=settings.REDIS_THREAD_TTL,
        )
    except Exception:
        logger.exception("Failed to set thread_id in Redis for %s", phone_number)
