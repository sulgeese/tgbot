import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from db.repositories import EventRepository
from bot.datetime_utils import format_datetime
from bot.handlers.private_router.utils import process_events
from bot.handlers.utils import send_events_list
from bot.keyboards import inline
from bot.states import StepsForm
from bot.validate.callback_check import ensure_callback_message


router = Router()


@router.callback_query(StepsForm.VIEW_EVENTS, F.data == "event_search_back")
@router.callback_query(F.data == "search_events")
async def view_event_list(call: CallbackQuery, session: AsyncSession, state: FSMContext, redis: Redis) -> None:
    await send_events_list(call, session, redis)
    await state.set_state(StepsForm.VIEW_EVENTS)


@ensure_callback_message
async def view_event(call: CallbackQuery, session: AsyncSession, redis: Redis) -> None:
    if call.data and (event := await EventRepository(session, redis).get(uuid.UUID(call.data[1:]))):
        await call.message.edit_text(  # type: ignore
            text=f"<i><b>{event.title}</b></i>\n{event.text}\n{event.mentions}\n\nБудет отправлено в {format_datetime(event.date)}",
            reply_markup=inline.event_back,
            parse_mode="HTML",
        )


router.callback_query(StepsForm.VIEW_EVENTS)(process_events(view_event))
