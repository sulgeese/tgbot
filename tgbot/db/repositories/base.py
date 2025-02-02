import logging
from typing import Optional, TypeVar, Type

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel


logger = logging.getLogger(__name__)

T = TypeVar("T")
P = TypeVar("P", bound=BaseModel)

class BaseRepository[T, P]:
    def __init__(self, db: AsyncSession, redis: Redis, model: Type[T], schema: Type[P]):
        self.db = db
        self.redis = redis
        self.model = model
        self.schema = schema

    async def create(self, data: P) -> Optional[P]:
        try:
            instance = self.model(**data.model_dump())
            self.db.add(instance)
            await self.db.commit()
            await self.db.refresh(instance)
            await self._cache_instance(instance)
            return self.schema.model_validate(instance)
        except Exception as err:
            await self.db.rollback()
            logger.error(f"Couldn't create {self.model.__name__} due to error: {err}")

    async def get(self, instance_id) -> Optional[P]:
        try:
            if instance := (await self._get_cached_instance(instance_id)):
                return instance
            if instance := (await self._get(instance_id)):
                await self._cache_instance(instance)
                return self.schema.model_validate(instance)
            logger.debug(f"{self.model.__name__} instance with id {instance_id} not found")
        except Exception as err:
            logger.error(f"Couldn't get {self.model.__name__} instance due to error: {err}")

    async def update(self, data: P) -> Optional[P]:
        try:
            instance = await self._get(data.id)
            for key, value in data.model_dump().items():
                setattr(instance, key, value)
            await self.db.commit()
            await self.db.refresh(instance)
            await self._cache_instance(instance)
            return self.schema.model_validate(instance)
        except Exception as err:
            await self.db.rollback()
            logger.error(f"Couldn't update {self.model.__name__} instance due to error: {err}")

    async def delete(self, instance_id) -> None:
        try:
            await self.db.delete(await self._get(instance_id))
            await self.db.commit()
            await self._delete_cached_instance(instance_id)
        except Exception as err:
            await self.db.rollback()
            logger.error(f"Couldn't delete {self.model.__name__} instance due to error: {err}")

    async def _get(self, instance_id) -> Optional[T]:
        try:
            return await self.db.get(self.model, instance_id)
        except Exception as err:
            logger.error(f"Couldn't get {self.model.__name__} instance due to error: {err}")

    async def _cache_instance(self, instance: T) -> None:
        try:
            await self.redis.hset(
                f"{self.model.__name__.lower()}:{instance.id}",
                mapping={k: str(v) for k, v in self.schema.model_validate(instance).model_dump().items()}
            )
        except Exception as err:
            logger.error(f"Couldn't cache {self.model.__name__} instance due to error: {err}")

    async def _get_cached_instance(self, instance_id: int) -> Optional[P]:
        try:
            cached_data = await self.redis.hgetall(f"{self.model.__name__.lower()}:{instance_id}")
            if cached_data:
                return self.schema(**{k.decode(): v.decode() for k, v in cached_data.items()})
        except Exception as err:
            logger.error(f"Couldn't get cached {self.model.__name__} instance due to error: {err}")

    async def _delete_cached_instance(self, instance_id: int) -> None:
        try:
            await self.redis.delete(f"{self.model.__name__.lower()}:{instance_id}")
        except Exception as err:
            logger.error(f"Couldn't delete cached {self.model.__name__} instance due to error: {err}")