from redis.asyncio import Redis

from src.settings import settings

redis = Redis(
    port=settings.redis.port,
    host=settings.redis.host,
)
