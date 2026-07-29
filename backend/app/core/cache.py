from typing import Optional, Any

redis_client: Optional[Any] = None


async def init_cache() -> None:
    global redis_client
    try:
        from redis.asyncio import Redis
        from app.core.config import settings
        redis_client = Redis.from_url(settings.redis_url, decode_responses=True)
    except ImportError:
        redis_client = None


async def close_cache() -> None:
    global redis_client
    if redis_client is not None:
        try:
            await redis_client.close()
        except Exception:
            pass
        redis_client = None


async def cache_get(key: str) -> Optional[str]:
    if redis_client is None:
        return None
    try:
        return await redis_client.get(key)
    except Exception:
        return None


async def cache_set(key: str, value: str, ttl: int = 300) -> None:
    if redis_client is None:
        return
    try:
        await redis_client.set(key, value, ex=ttl)
    except Exception:
        pass
