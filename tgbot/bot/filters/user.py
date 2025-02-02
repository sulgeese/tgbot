from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, ChatMember

from db.redis_instance import redis
from db.repositories.user import UserRepository


class UserInGroup(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, obj: TelegramObject, session: AsyncSession) -> bool:
        if isinstance(obj, ChatMember):
            user_id = obj.new_chat_member.user.id
        else:
            user_id = obj.from_user.id
        return (await UserRepository(session, redis).get(user_id)).in_group
