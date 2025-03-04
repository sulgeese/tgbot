import logging
from typing import Optional, Type, Any

from redis.asyncio import Redis
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession


logger = logging.getLogger(__name__)


class BaseRepository[T: SQLModel]:
    def __init__(self, db: AsyncSession, redis: Redis, model: Type[T], id_name: str):
        self.db = db
        self.redis= redis
        self.model = model
        self.id_name = id_name

    async def create(self, instance: T) -> Optional[T]:
        try:
            self.db.add(instance)
            await self.db.commit()
            await self.db.refresh(instance)
            await self._cache_instance(instance)
            return instance
        except Exception as err:
            await self.db.rollback()
            logger.error(f"Couldn't create {self.model.__name__} due to error: {err}")
        return None

    async def get(self, instance_id: Any) -> Optional[T]:
        try:
            if instance := (await self._get_cached_instance(instance_id)):
                return instance
            if instance := (await self.db.get(self.model, instance_id)):
                await self._cache_instance(instance)
                return instance
            logger.debug(f"{self.model.__name__} instance with id {instance_id} not found")
        except Exception as err:
            logger.error(f"Couldn't get {self.model.__name__} instance due to error: {err}")
        return None

    async def update(self, instance: T) -> Optional[T]:
        try:
            updated_instance = instance.sqlmodel_update(instance)
            instance = await self.db.merge(updated_instance)
            await self.db.commit()
            await self.db.refresh(instance)
            await self._cache_instance(instance)
            return instance
        except Exception as err:
            await self.db.rollback()
            logger.error(f"Couldn't update {self.model.__name__} instance due to error: {err}")
        return None

    async def delete(self, instance_id: Any) -> None:
        try:
            instance = await self.db.get(self.model, instance_id)
            await self.db.delete(instance)
            await self.db.commit()
            await self._delete_cached_instance(instance_id)
        except Exception as err:
            await self.db.rollback()
            logger.error(f"Couldn't delete {self.model.__name__} instance due to error: {err}")
        return None

    async def _cache_instance(self, instance: T) -> None:
        try:
            await self.redis.hset(  # type: ignore
                f"{self.model.__name__.lower()}:{getattr(instance, self.id_name)}",
                mapping={k: str(v) for k, v in instance.model_dump().items()}
            )
        except Exception as err:
            logger.error(f"Couldn't cache {self.model.__name__} instance due to error: {err}")

    async def _get_cached_instance(self, instance_id: Any) -> Optional[T]:
        try:
            if cached_data := await self.redis.hgetall(f"{self.model.__name__.lower()}:{instance_id}"):  # type: ignore
                instance = self.model.model_validate({k.decode(): v.decode() for k, v in cached_data.items()})
                return instance
        except Exception as err:
            logger.error(f"Couldn't get cached {self.model.__name__} instance due to error: {err}")
        return None

    async def _delete_cached_instance(self, instance_id: Any) -> None:
        try:
            await self.redis.delete(f"{self.model.__name__.lower()}:{instance_id}")
        except Exception as err:
            logger.error(f"Couldn't delete cached {self.model.__name__} instance due to error: {err}")

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({repr(self.model)})"