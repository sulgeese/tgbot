import logging
from typing import TypedDict, Optional, List, cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, ConfigDict

from settings import Redis
from .base import BaseRepository
from db.models import UsersModel


logger = logging.getLogger(__name__)

# class UserCreateArgs(TypedDict):
#     id: int
#     username: Optional[str]
#     first_name: Optional[str]
#     last_name: Optional[str]
#     in_group: bool
#
# class UserUpdateArgs(TypedDict):
#     id: int
#     username: Optional[str]
#     first_name: Optional[str]
#     last_name: Optional[str]
#     in_group: Optional[bool]

class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    in_group: Optional[bool] = True


class UserRepository(BaseRepository[UsersModel, User]):
    def __init__(self, db: AsyncSession, redis: Redis):
        super().__init__(db, redis, UsersModel, User)

    # async def create(self, **kwargs: UserCreateArgs) -> Optional[UsersModel]:
    #     return await super().create(**kwargs)
    #
    # async def get(self, user_id: int) -> Optional[UsersModel]:
    #     return await super().get(user_id)
    #
    # async def update(self, **kwargs: UserUpdateArgs) -> Optional[UsersModel]:
    #     return await super().update(**kwargs)
    #
    # async def delete(self, user_id: int) -> Optional[UsersModel]:
    #     return await super().delete(user_id)

    async def get_users_in_group(self) -> Optional[List[UsersModel]]:
        try:
            query = (
                select(UsersModel)
                .filter(UsersModel.in_group)
            )
            results = await self.db.execute(query)
            return cast(List[UsersModel], results.scalars().all())
        except Exception as err:
            logger.error(f"Cannot get users in group: {err}")