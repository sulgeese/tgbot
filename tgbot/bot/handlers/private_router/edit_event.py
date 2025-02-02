from typing import Any
import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.handlers import bot_messages
from bot.keyboard import inline
from bot.states import StepsForm
from db.redis_instance import redis
from db.repositories.event import EventRepository
from db.repositories.user import UserRepository
from utils import format_datetime
from .utils import get_date, get_mentions, get_title, get_text, handle_event_update

router = Router()


# Entrypoint to start editing
@router.callback_query(F.data == "edit_events")
async def edit_events_list(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.EDIT_EVENTS)


# Handle an event to edit
@router.callback_query(StepsForm.EDIT_EVENTS, F.data.startswith("$"))
async def edit_event(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await EventRepository(session, redis).get(uuid.UUID(call.data[1:]))
    print(data)
    await state.update_data(
        id=str(data.id),
        title=data.title,
        date=format_datetime(data.date),
        text=data.text,
        mentions=data.mentions
    )
    await call.message.edit_text(
        text="<b>Что изменить?</b>",
        parse_mode="HTML",
        reply_markup=inline.edit_events,
    )


# Gets title from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_title")
async def edit_title(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.edit_text(
        text='<b>Текущее название: <code>{}</code>\nВведите новое</b>'
        .format(data["title"]),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_GET_TITLE)


async def on_success_title(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Название изменено ✅</b>",
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS)
    await bot_messages.send_edit_event_message(message=message, state=state)


router.message(StepsForm.EDIT_GET_TITLE, F.text)(get_title(on_success_title))


# Gets date from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_date")
async def get_date_message(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.edit_text(
        text="Текущая дата: <code>{}</code>\n<b>Введите новую</b>"
        .format(data["date"]),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_GET_DATE)


async def on_success_date(message: Message, state: FSMContext) -> Any:
    await state.update_data(date=message.text)
    await message.answer(
        text="<b>Дата изменена ✅</b>",
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS)
    await bot_messages.send_edit_event_message(message=message, state=state)


router.message(StepsForm.EDIT_GET_DATE, F.text)(get_date(on_success_date))


# Gets text from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_text")
async def edit_text(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.edit_text(
        text='<b>Текущий текст: <code>{}</code>\nВведите новый</b>'
        .format(data["text"]),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_GET_TEXT)


async def on_success_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await message.answer(
        text="<b>Текст уведомления изменён ✅</b>",
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS)
    await bot_messages.send_edit_event_message(message=message, state=state)


router.message(StepsForm.EDIT_GET_TEXT, F.text)(get_text(on_success_text))


# Gets mentions from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_mentions")
async def edit_mentions(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    await state.update_data(mentions="")
    users = await UserRepository(session, redis).get_users_in_group()
    await call.message.edit_text(
        text='<b>Сейчас отмечены: {}\nКого отметить?</b>'
        .format(data["mentions"]),
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )
    await state.set_state(StepsForm.EDIT_GET_MENTIONS)


async def on_success_mentions(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        text='<b>Упоминания изменены ✅</b>',
        parse_mode="HTML",
    )
    await bot_messages.send_edit_event_message(message=call.message, state=state)


router.callback_query(StepsForm.EDIT_GET_MENTIONS)(get_mentions(on_success_mentions))


# Saves or doesn't save the event and sends start menu
async def on_event_save_confirmation(call: CallbackQuery) -> Any:
    await call.message.edit_text(
        text="<b>Событие обновлено ✅</b>",
        parse_mode="HTML",
    )


async def on_event_save_cancellation(call: CallbackQuery) -> Any:
    await call.message.edit_text(
        text="<b>Действие отменено ❌</b>",
        parse_mode="HTML",
    )


router.callback_query(StepsForm.EDIT_EVENTS, F.data == "confirm")(
    handle_event_update(on_event_save_confirmation, on_event_save_cancellation))
router.callback_query(StepsForm.EDIT_EVENTS, F.data == "cancel")(
    handle_event_update(on_event_save_confirmation, on_event_save_cancellation))
