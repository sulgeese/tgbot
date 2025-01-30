from datetime import datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.date import DateNotPassed, DateFilter
from bot.filters.user import UserInGroup
from bot.handlers import bot_messages
from bot.keyboard import inline, reply
from bot.states import StepsForm
from db import requests
from utils import format_datetime

router = Router()


@router.callback_query(F.data == "cancel_event")
@router.callback_query(F.data == "search_events")
async def search_events(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.VIEW_EVENTS)

@router.callback_query(StepsForm.VIEW_EVENTS, F.data.startswith("$"))
async def search_events(call: CallbackQuery, session: AsyncSession) -> None:
    data = await requests.select_event(session=session, event_id=int(call.data[1:]))
    title, text, mentions, date = data.get("title"), data.get("text"), data.get("mentions"), data.get("date")
    await call.message.edit_text(
        text=f"<i><b>{title}</b></i>\n{text}\n{mentions}\n\nБудет отправлено в {date}",
        reply_markup=inline.event_search_back,
        parse_mode="HTML",
    )

@router.callback_query(F.data == "back")
async def start_menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(
        text="<b>Что хотите сделать?</b>",
        reply_markup=inline.events,
        parse_mode="HTML"
    )