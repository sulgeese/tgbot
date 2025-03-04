import logging
from typing import Optional, List

from redis.asyncio import Redis
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.repositories.base import BaseRepository
from db.models import UsersModel


logger = logging.getLogger(__name__)


class UserRepository(BaseRepository[UsersModel]):
    def __init__(self, db: AsyncSession, redis: Redis):
        super().__init__(db, redis, UsersModel, "id")

    async def create(self, user: UsersModel) -> Optional[UsersModel]:
        return await super().create(user)

    async def get(self, user_id: int) -> Optional[UsersModel]:
        return await super().get(instance_id=user_id)

    async def update(self, user: UsersModel) -> Optional[UsersModel]:
        return await super().update(user)

    async def delete(self, user_id: int) -> None:
        return await super().delete(user_id)

    async def get_users_in_group(self) -> Optional[List[UsersModel]]:
        try:
            results = await self.db.exec(select(UsersModel).where(UsersModel.in_group == True))
            return results.all()
        except Exception as err:
            logger.error(f"Cannot get users in group: {err}")
            return None