import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from db.redis_instance import redis
from db.repositories.event import EventRepository
from utils import format_datetime
from .utils import process_events
from bot.handlers import bot_messages
from bot.keyboard import inline
from bot.states import StepsForm

router = Router()


@router.callback_query(StepsForm.VIEW_EVENTS, F.data == "event_search_back")
@router.callback_query(F.data == "search_events")
async def view_event_list(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.VIEW_EVENTS)


async def view_event(call: CallbackQuery, session: AsyncSession) -> None:
    event = await EventRepository(session, redis).get(uuid.UUID(call.data[1:]))
    await call.message.edit_text(
        text=f"<i><b>{event.title}</b></i>\n{event.text}\n{event.mentions}\n\nБудет отправлено в {format_datetime(event.date)}",
        reply_markup=inline.event_back,
        parse_mode="HTML",
    )


router.callback_query(StepsForm.VIEW_EVENTS)(process_events(view_event))
