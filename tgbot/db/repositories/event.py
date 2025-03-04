import logging
from uuid import UUID
from typing import Optional, List
from datetime import datetime, timedelta

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
from sqlmodel import select, asc
from sqlmodel.ext.asyncio.session import AsyncSession

from db.repo.base import BaseRepository
from db.models import EventsModel


logger = logging.getLogger(__name__)


class EventRepository(BaseRepository[EventsModel]):
    def __init__(self, db: AsyncSession, redis: Redis, scheduler: AsyncIOScheduler = None):
        self.scheduler = scheduler
        super().__init__(db, redis, EventsModel)

    async def create(self, event: EventsModel) -> Optional[EventsModel]:
        result = await super().create(event)
        if result:
            await self._add_job(result)
        return result

    async def get(self, event_id: UUID) -> Optional[EventsModel]:
        return await super().get(event_id)

    async def update(self, event: EventsModel) -> Optional[EventsModel]:
        result = await super().update(event)
        if result:
            await self._remove_job(result.id)
            await self._add_job(result)
        return result


    async def delete(self, event_id: UUID) -> None:
        await self._remove_job(event_id)
        await super().delete(event_id)

    async def get_events_by_user(self, user_id: int) -> Optional[List[EventsModel]]:
        try:
            query = (
                select(EventsModel)
                .where(EventsModel.date >= datetime.today(), EventsModel.user_id == user_id)
                .order_by(asc(EventsModel.date))
            )
            results = await self.db.exec(query)
            return results.all()
        except Exception as err:
            logger.error(f"Cannot get events for user {user_id}: {err}")

    async def _remove_job(self, event_id: UUID) -> None:
        try:
            self.scheduler.remove_job(str(event_id))
        except Exception as err:
            logger.warning(f"Couldn't remove job with id {event_id} due to error: {err}")

    async def _add_job(self, event: EventsModel) -> None:
        try:
            from bot.handlers.utils import send_message
            self.scheduler.add_job(
                id=str(event.id),
                func=send_message,
                trigger="date",
                run_date=max(event.date, datetime.now() + timedelta(seconds=10)),
                kwargs={"title": event.title, "text": event.text, "mentions": event.mentions}
            )
        except Exception as err:
            logger.error("Couldn't add job to scheduler due to error: %s", err)