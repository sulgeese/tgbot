import pickle
from contextlib import suppress
from datetime import datetime
from typing import AnyStr, List

from sqlalchemy import select, asc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.models import GroupUsersModel, EventsModel
from src.db.redis import redis


async def insert_user_into_group(session: AsyncSession, user_id: int, username: str, first_name: str | None,
                                 last_name: str | None) -> None:
    user = await session.get(GroupUsersModel, user_id)
    if not user:
        user = GroupUsersModel()
    user.user_id = user_id
    user.username = username
    user.first_name = first_name
    user.last_name = last_name
    user.in_group = True
    await session.merge(user)
    with suppress(IntegrityError):
        await session.commit()


async def del_user_from_group(session: AsyncSession, user_id: int) -> None:
    user = await session.get(GroupUsersModel, user_id)
    user.in_group = False
    with suppress(IntegrityError):
        await session.commit()


async def is_user_in_group(session: AsyncSession, user_id: str) -> bool:
    if not await redis.exists('users'):
        data = await session.execute(select(GroupUsersModel))
        data = [str(user.user_id) for user in data.scalars().all() if user.in_group]
        if data:
            await redis.lpush('users', *data)
    return not (await redis.lpos('users', user_id) is None)


async def get_users_in_group(session: AsyncSession) -> List:
    data = await session.execute(select(GroupUsersModel))
    data = [(user.first_name + (f" {user.last_name}" if user.last_name else ""), user.user_id)
            for user in data.scalars().all() if user.in_group]
    return data


async def insert_event(session: AsyncSession, date: datetime, text: str, user_id: int) -> None:
    event = EventsModel()
    event.date = date
    event.text = text
    event.user_id = user_id
    await session.merge(event)
    await redis.delete('events')
    with suppress(IntegrityError):
        await session.commit()


async def select_current_events(session: AsyncSession) -> [[datetime, AnyStr]]:
    if not await redis.exists('events'):
        today = datetime.today()
        data = await session.execute(
            select(EventsModel.date, EventsModel.text)
            .filter(EventsModel.date >= today)
            .order_by(asc(EventsModel.date))
        )
        data = [(row.date, row.text) for row in data]
        await redis.set('events', pickle.dumps(data), ex=60)
        return data
    data = await redis.get('events')
    return pickle.loads(data)
