from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession
from aiogram.filters import BaseFilter
from aiogram import types

from db.repositories import UserRepository


class UserInGroup(BaseFilter):
    def __init__(self) -> None:
        pass

    async def __call__(self, obj: types.TelegramObject, session: AsyncSession, redis: Redis) -> bool:
        if isinstance(obj, (types.Message, types.CallbackQuery, types.InlineQuery, types.ChosenInlineResult,
                            types.ShippingQuery, types.PreCheckoutQuery)):
            if obj.from_user:
                user_id = obj.from_user.id
                if user := (await UserRepository(session, redis).get(user_id)):
                    return user.in_group
        return True
