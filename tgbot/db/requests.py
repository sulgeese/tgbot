import json
import logging
from contextlib import suppress
from datetime import datetime
from typing import AnyStr, List, Optional, Tuple

from apscheduler.jobstores.base import JobLookupError
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy import select, asc, desc
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import GroupUsersModel, EventsModel
from db.redis_instance import redis
from utils import datetime_to_str, str_to_datetime


USERS_KEY = "users"
EVENTS_KEY = "events"

logging = logging.getLogger(__name__)


async def cache_in_redis(key: str, redis_data: dict) -> None:
    await redis.hset(key, mapping={str(k): json.dumps(v, ensure_ascii=False) for k, v in redis_data.items()})
    return None


def serialize_user(user: GroupUsersModel) -> dict:
    return {
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "in_group": user.in_group,
    }


def serialize_event(event: EventsModel) -> dict:
    return {
        "title": event.title,
        "date": datetime_to_str(event.date),
        "text": event.text,
        "mentions": event.mentions,
        "user_id": event.user_id,
    }


async def cache_users_in_redis(session: AsyncSession) -> bool:
    if not await redis.exists(USERS_KEY):
        users = await session.execute(select(GroupUsersModel))
        user_data = {user.user_id: serialize_user(user) for user in users.scalars().all()}
        await cache_in_redis(USERS_KEY, user_data)
    return True


async def cache_events_in_redis(session: AsyncSession) -> bool:
    if not await redis.exists(EVENTS_KEY):
        today = datetime.today()
        events = await session.execute(
            select(EventsModel)
            .filter(EventsModel.date >= today)
            .order_by(asc(EventsModel.date))
        )
        event_data = {event.id: serialize_event(event) for event in events.scalars().all()}
        if not event_data:
            return False
        await cache_in_redis(EVENTS_KEY, event_data)
    return True


async def update_user_status(
        session: AsyncSession,
        user_id: int,
        in_group: bool,
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
) -> None:
    user = await session.get(GroupUsersModel, user_id) or GroupUsersModel(user_id=user_id)
    user.username, user.first_name, user.last_name, user.in_group = username, first_name, last_name, in_group
    await session.merge(user)
    with suppress(IntegrityError):
        await session.commit()
    if await redis.exists(USERS_KEY):
        await redis.delete(USERS_KEY)


async def check_user_existence(session: AsyncSession, user_id: str) -> bool:
    if await cache_users_in_redis(session):
        return await redis.hexists(USERS_KEY, user_id)


async def get_users_in_group(session: AsyncSession) -> List[Tuple[str, str]]:
    if await cache_users_in_redis(session):
        user_data = []
        users = await redis.hvals(USERS_KEY)
        for user in map(json.loads, users):
            if user.get("in_group"):
                if user.get("last_name"):
                    user_data.append((f"{user["first_name"]} {user["last_name"]}", user["username"]))
                else:
                    user_data.append((user["first_name"], user["username"]))
        return user_data


async def delete_event(session: AsyncSession, scheduler: AsyncIOScheduler, event_id: int | str) -> None:
    try:
        scheduler.remove_job(str(event_id), "default")
    except JobLookupError as err:
        logging.warning(err)
    if await redis.exists(EVENTS_KEY):
        await redis.delete(EVENTS_KEY)
    if event := await session.get(EventsModel, event_id):
        await session.delete(event)
        with suppress(IntegrityError):
            await session.commit()


async def edit_event(
        session: AsyncSession,
        scheduler: AsyncIOScheduler,
        event_id: int,
        title: str,
        date: datetime,
        text: str, mentions: str
) -> None:
    event = await session.get(EventsModel, event_id)
    event.title, event.date, event.text, event.mentions = title, date, text, mentions
    await delete_event(session, scheduler, event_id)
    await session.merge(event)
    with suppress(IntegrityError):
        await session.commit()
    if await redis.exists(EVENTS_KEY):
        await redis.delete(EVENTS_KEY)


async def insert_event(
        session: AsyncSession,
        title: str,
        date: datetime,
        text: str,
        user_id: int,
        mentions: str
) -> None:
    event = EventsModel()
    event.title, event.date, event.text, event.mentions, event.user_id = title, date, text, mentions, user_id
    await session.merge(event)
    with suppress(IntegrityError):
        await session.commit()
    if await redis.exists(EVENTS_KEY):
        await redis.delete(EVENTS_KEY)



async def select_current_events(session: AsyncSession) -> [[datetime, AnyStr]]:
    if await cache_events_in_redis(session):
        events = await redis.hvals(EVENTS_KEY)
        return [
            (str_to_datetime(event["date"]), event["text"])
            for event in (json.loads(e) for e in events)
        ]


async def select_current_users_events(session: AsyncSession, user_id: int) -> [[datetime, AnyStr]]:
    if await cache_events_in_redis(session):
        data = []
        events_id = await redis.hkeys("events")
        for event_id in events_id:
            event = await redis.hget("events", event_id)
            event = json.loads(event)
            if event.get("user_id") == int(user_id):
                event_id = event_id.decode('utf-8')
                data.append({"event_id": event_id, "title": event.get("title")})
        return data


async def select_event(session: AsyncSession, event_id: int):
    if await cache_events_in_redis(session):
        event = await redis.hget("events", str(event_id))
        event = json.loads(event)
        data = {"event_id": event_id,
                "title": event.get("title"),
                "date": event.get("date"),
                "text": event.get("text"),
                "user_id": event.get("user_id"),
                "mentions": event.get("mentions")
                }
        return data


async def get_event_id(session: AsyncSession, title: str):
    event_id = await session.execute(
        select(EventsModel.id)
        .filter(EventsModel.title == title)
        .order_by(desc(EventsModel.id))
    )
    return event_id.scalars().one()
