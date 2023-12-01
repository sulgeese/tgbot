from bot.settings import settings

from redis.asyncio import Redis

redis = Redis(
    port=settings.redis.port,
    host=settings.redis.host,
)
