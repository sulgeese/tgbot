from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from bot.db.models import GroupUsersModel
from bot.db.models import EventsModel
from bot.db.redis import redis

from contextlib import suppress
from datetime import datetime


async def insert_user(session: AsyncSession, user_id: int, username: str, first_name: str | None,
                      last_name: str | None) -> None:
    user = GroupUsersModel()
    user.user_id = user_id
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    await session.merge(user)
    with suppress(IntegrityError):
        await session.commit()


async def del_user(session: AsyncSession, user_id: int) -> None:
    user = await session.get(GroupUsersModel, user_id)
    await session.delete(user)
    with suppress(IntegrityError):
        await session.commit()


async def user_in_group(session: AsyncSession, user_id: str) -> bool:
    if not await redis.exists('users'):
        data = await session.execute(select(GroupUsersModel))
        data = [str(user.user_id) for user in data.scalars().all()]
        await redis.lpush('users', *data)
    return not (await redis.lpos('users', user_id) is None)


async def insert_event(session: AsyncSession, date: datetime, text: str, user_id: int) -> None:
    event = EventsModel()
    event.date = date
    event.text = text
    event.user_id = user_id
    await session.merge(event)
    with suppress(IntegrityError):
        await session.commit()
