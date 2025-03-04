import logging

from redis.asyncio import Redis

from settings import settings


logger = logging.getLogger(__name__)

try:
    redis = Redis(
        host=settings.redis.host,
        port=settings.redis.port,
    )
except Exception as err:
    logger.error(f"Redis connection failed: {err}")
    raise


