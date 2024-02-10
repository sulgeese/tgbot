import pickle
from contextlib import suppress
from datetime import datetime
from typing import AnyStr, List

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import GroupUsersModel, EventsModel
from db.redis import redis


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
    if user:
        user.in_group = False
        with suppress(IntegrityError):
            await session.commit()


async def is_user_in_group(session: AsyncSession, user_id: str) -> bool:
    if not await redis.exists("users"):
        data = await session.execute(select(GroupUsersModel))
        data = [str(user.user_id) for user in data.scalars().all() if user.in_group]
        if data:
            await redis.lpush("users", *data)
    return not (await redis.lpos("users", str(user_id)) is None)


async def get_users_in_group(session: AsyncSession) -> List:
    data = await session.execute(select(GroupUsersModel))
    data = [(user.first_name + (f" {user.last_name}" if user.last_name else ""), user.username)
            for user in data.scalars().all() if user.in_group]
    return data


async def delete_event(session: AsyncSession, scheduler: AsyncIOScheduler, event_id: int | str) -> None:
    try:
        scheduler.remove_job(str(event_id), "default")
    except JobLookupError:
        pass
    if await redis.exists("events"):
        await redis.delete("events")
    event = await session.get(EventsModel, event_id)
    if event:
        await session.delete(event)
        with suppress(IntegrityError):
            await session.commit()


async def edit_event(session: AsyncSession, scheduler: AsyncIOScheduler, event_id: int, title: str, date: datetime,
                     text: str, mentions: str) -> None:
    event = await session.get(EventsModel, event_id)
    if title: event.title = title
    if date: event.date = date
    if text: event.text = text
    if mentions: event.mentions = mentions
    await delete_event(session, scheduler=scheduler, event_id=event_id)
    await session.merge(event)
    with suppress(IntegrityError):
        await session.commit()


async def insert_event(session: AsyncSession, title: str, date: datetime, text: str, user_id: int,
                       mentions: str) -> None:
    event = EventsModel()
    event.title = title
    event.date = date
    event.text = text
    event.user_id = user_id
    event.mentions = mentions
    await session.merge(event)
    if await redis.exists("events"):
        await redis.delete("events")
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


async def select_current_users_events(session: AsyncSession, user_id: int) -> List:
    today = datetime.today()
    data = await session.execute(
        select(EventsModel)
        .filter(EventsModel.user_id == user_id)
        .filter(EventsModel.date >= today)
        .order_by(asc(EventsModel.date))
    )
    return data.scalars().all()


async def select_event(session: AsyncSession, event_id: int):
    if not await redis.exists(str(event_id)):
        event = await session.execute(
            select(EventsModel)
            .filter(EventsModel.id == event_id)
        )
        event = event.scalars().one()
        data = {"id": event.id, "title": event.title, "date": event.date, "text": event.text, "user_id": event.user_id,
                "mentions": event.mentions}
        await redis.set(str(event_id), pickle.dumps(data), ex=60)
        return data
    data = await redis.get(str(event_id))
    return pickle.loads(data)


async def get_event_id(session: AsyncSession, title: str):
    event_id = await session.execute(
        select(EventsModel.id)
        .filter(EventsModel.title == title)
        .order_by(desc(EventsModel.id))
    )
    return event_id.scalars().one()
