from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject
from aiogram.types import ChatMember

from bot.db.requests import get_users_in_group


class UserInGroup(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, obj: TelegramObject, session: AsyncSession) -> bool:
        if isinstance(obj, ChatMember):
            user_id = obj.new_chat_member.user.id
        else:
            user_id = obj.from_user.id
        return user_id in await get_users_in_group(session)


class UserNotInGroup(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, obj: TelegramObject, session: AsyncSession) -> bool:
        if isinstance(obj, ChatMember):
            user_id = obj.new_chat_member.user.id
        else:
            user_id = obj.from_user.id
        return user_id not in await get_users_in_group(session)
