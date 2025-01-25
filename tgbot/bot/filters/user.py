from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import BaseFilter
from aiogram.types import TelegramObject, ChatMember

from db.requests import check_user_existence


class UserInGroup(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, obj: TelegramObject, session: AsyncSession) -> bool:
        if isinstance(obj, ChatMember):
            user_id = obj.new_chat_member.user.id
        else:
            user_id = obj.from_user.id
        return await check_user_existence(session, str(user_id))


class UserNotInGroup(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, obj: TelegramObject, session: AsyncSession) -> bool:
        if isinstance(obj, ChatMember):
            user_id = obj.new_chat_member.user.id
        else:
            user_id = obj.from_user.id
        return not await check_user_existence(session, str(user_id))
