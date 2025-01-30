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


@router.callback_query(F.data == "delete_events")
async def delete_event_list(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.DELETE_EVENTS)

@router.callback_query(F.data.startswith("$"), StepsForm.DELETE_EVENTS)
async def delete_event(call: CallbackQuery, session: AsyncSession, scheduler: AsyncIOScheduler) -> None:
    await requests.delete_event(session=session, scheduler=scheduler, event_id=int(call.data[1:]))
    await bot_messages.send_events_list(call=call, session=session)

@router.callback_query(F.data == "back")
async def start_menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(
        text="<b>Что хотите сделать?</b>",
        reply_markup=inline.events,
        parse_mode="HTML"
    )