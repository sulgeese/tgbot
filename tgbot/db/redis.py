from redis.asyncio import Redis

from settings import settings

redis = Redis(
    port=settings.redis.port,
    host=settings.redis.host,
)
