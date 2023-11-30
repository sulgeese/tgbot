from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy import select

from bot.db.models import GroupUsersModel
from bot.db.models import EventsModel
from bot.misc import redis

from contextlib import suppress
from datetime import datetime
import json


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


async def get_users_in_group(session: AsyncSession) -> list:
    if await redis.get("users") is None:
        users = await session.execute(select(GroupUsersModel))
        data = [user.user_id for user in users.scalars().all()]
        await redis.set('users', json.dumps(data))
    res = await redis.get("users")
    return json.loads(res)


async def insert_event(session: AsyncSession, date: datetime, text: str, user_id: int) -> None:
    event = EventsModel()
    event.date = date
    event.text = text
    event.user_id = user_id
    await session.merge(event)
    with suppress(IntegrityError):
        await session.commit()
