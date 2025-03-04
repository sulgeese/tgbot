import logging
import uuid
from typing import Any

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from bot.handlers.private_router.utils import process_events
from bot.handlers.utils import send_events_list
from bot.states import StepsForm
from bot.validate.callback_check import ensure_callback_message
from db.repositories import EventRepository


logger = logging.getLogger(__name__)

router = Router()


@router.callback_query(F.data == "delete_events")
async def delete_event_list(call: CallbackQuery, session: AsyncSession, state: FSMContext, redis: Redis) -> None:
    await send_events_list(call, session, redis)
    await state.set_state(StepsForm.DELETE_EVENTS)


@ensure_callback_message
async def delete_event(call: CallbackQuery, session: AsyncSession, scheduler: AsyncIOScheduler, redis: Redis) -> Any:
    if call.data:
        await EventRepository(session, redis, scheduler).delete(uuid.UUID(call.data[1:]))
        return await send_events_list(call, session, redis)
    logger.warning(f"Failed to get data from CallbackQuery")


router.callback_query(StepsForm.DELETE_EVENTS)(process_events(delete_event))
