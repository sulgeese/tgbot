import logging
import uuid
from typing import Optional, List, cast, Tuple
from datetime import datetime

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select, asc
from sqlalchemy.ext.asyncio import AsyncSession

from settings import Redis
from .base import BaseRepository
from db.models import EventsModel


logger = logging.getLogger(__name__)


class Event(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    title: Optional[str] = None
    date: Optional[datetime] = None
    text: Optional[str] = None
    user_id: Optional[int] = None
    mentions: Optional[str] = None


class EventRepository(BaseRepository[EventsModel, Event]):
    def __init__(self, db: AsyncSession, redis: Redis):
        super().__init__(db, redis, EventsModel, Event)

    async def create(self, data: Event) -> Optional[Event]:
        return await super().create(data)

    async def get(self, event_id: uuid.UUID) -> Optional[Event]:
        return await super().get(event_id)

    async def update(self, data: Event) -> Optional[Event]:
        return await super().update(data)

    async def delete(self, event_id: uuid.UUID) -> Optional[Event]:
        return await super().delete(event_id)

    async def get_events_by_user(self, user_id: int) -> Optional[List[EventsModel]]:
        try:
            query = (
                select(EventsModel)
                .filter(EventsModel.date >= datetime.today(), EventsModel.user_id == user_id)
                .order_by(asc(EventsModel.date))
            )
            results = await self.db.execute(query)
            return results.scalars().all()
        except Exception as err:
            logger.error(f"Cannot get events for user {user_id}: {err}")

    # async def _cache_events_by_user(self, ):
    #     try:
    #
    #     except Exception as err:
    #         logger.error("Cannot cache events by user: %s", err)
