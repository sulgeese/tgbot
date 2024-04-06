import json
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
from utils import datetime_to_str, str_to_datetime


async def set_users(session: AsyncSession) -> bool:
    if not await redis.exists("users"):
        users = await session.execute(select(GroupUsersModel))
        for user in users.scalars().all():
            data = {"username": user.username, "first_name": user.first_name, "last_name": user.last_name,
                    "in_group": user.in_group}
            await redis.hset("users", str(user.user_id), json.dumps(data, ensure_ascii=False))
    return True


async def set_events(session: AsyncSession) -> bool:
    if not await redis.exists("events"):
        today = datetime.today()
        events = await session.execute(
            select(EventsModel)
            .filter(EventsModel.date >= today)
            .order_by(asc(EventsModel.date))
        )
        for event in events.scalars().all():
            data = {"title": event.title, "date": datetime_to_str(event.date), "text": event.text,
                    "mentions": event.mentions, "user_id": event.user_id}
            await redis.hset("events", str(event.id), json.dumps(data, ensure_ascii=False))
    return True


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
    if await redis.exists("users"):
        await redis.delete("users")
    with suppress(IntegrityError):
        await session.commit()


async def del_user_from_group(session: AsyncSession, user_id: int) -> None:
    user = await session.get(GroupUsersModel, user_id)
    if user:
        user.in_group = False
        if await redis.exists("users"):
            await redis.delete("users")
        with suppress(IntegrityError):
            await session.commit()


async def is_user_in_group(session: AsyncSession, user_id: str) -> bool:
    if await set_users(session):
        return await redis.hexists("users", user_id)


async def get_users_in_group(session: AsyncSession) -> List:
    if await set_users(session):
        data = []
        users_id = await redis.hkeys("users")
        for user_id in users_id:
            user = await redis.hget("users", user_id)
            user = json.loads(user)
            if user.get("in_group"):
                first_name, last_name, username = user.get("first_name"), user.get("last_name"), user.get("username")
                if last_name:
                    data.append((f"{first_name} {last_name}", username))
                else:
                    data.append((first_name, username))
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
    event.title = title
    event.date = date
    event.text = text
    event.mentions = mentions
    await delete_event(session, scheduler=scheduler, event_id=event_id)
    await session.merge(event)
    if await redis.exists("events"):
        await redis.delete("events")
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
    if await set_events(session):
        data = []
        events_id = await redis.hkeys("events")
        for event_id in events_id:
            event = await redis.hget("events", event_id)
            event = json.loads(event)
            date, text = str_to_datetime(event.get("date")), event.get("text")
            data.append((date, text))
        return data


async def select_current_users_events(session: AsyncSession, user_id: int) -> [[datetime, AnyStr]]:
    if await set_events(session):
        data = []
        events_id = await redis.hkeys("events")
        for event_id in events_id:
            event = await redis.hget("events", event_id)
            event = json.loads(event)
            if event.get("user_id") == int(user_id):
                event_id = event_id.decode('utf-8')
                data.append({"event_id": event_id, "title": event.get("title")})
        return data


async def select_event(session: AsyncSession, event_id: str):
    if await set_events(session):
        event = await redis.hget("events", str(event_id))
        event = json.loads(event)
        data = {"event_id": str(event_id), "title": event.get("title"), "date": event.get("date"),
                "text": event.get("text"), "user_id": event.get("user_id"), "mentions": event.get("mentions")}
        return data


async def get_event_id(session: AsyncSession, title: str):
    event_id = await session.execute(
        select(EventsModel.id)
        .filter(EventsModel.title == title)
        .order_by(desc(EventsModel.id))
    )
    return event_id.scalars().one()
