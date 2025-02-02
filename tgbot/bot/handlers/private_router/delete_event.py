import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from db.redis_instance import redis
from db.repositories.event import EventRepository
from .utils import process_events
from bot.handlers import bot_messages
from bot.states import StepsForm

router = Router()


@router.callback_query(F.data == "delete_events")
async def delete_event_list(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.DELETE_EVENTS)


async def delete_event(call: CallbackQuery, session: AsyncSession, scheduler: AsyncIOScheduler) -> None:
    await EventRepository(session, redis).delete(uuid.UUID(call.data[1:]))
    await bot_messages.send_events_list(call=call, session=session)


router.callback_query(StepsForm.DELETE_EVENTS)(process_events(delete_event))
