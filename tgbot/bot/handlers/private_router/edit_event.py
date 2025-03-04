import logging
from typing import Any
import uuid

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from bot.handlers.private_router.utils import get_date, get_mentions, get_title, get_text, handle_event_update, process_events
from bot.handlers.utils import send_edit_event_message, send_events_list
from bot.keyboards import inline
from bot.states import StepsForm
from bot.validate.callback_check import ensure_callback_message
from db.repositories import EventRepository, UserRepository
from db.models import EventsModel
from bot.datetime_utils import normalize_datetime

router = Router()

logger = logging.getLogger(__name__)


# Entrypoint to start editing
@router.callback_query(F.data == "edit_events")
@ensure_callback_message
async def edit_events_list(call: CallbackQuery, state: FSMContext, session: AsyncSession, redis: Redis) -> None:
    await send_events_list(call, session, redis)
    await state.set_state(StepsForm.EDIT_EVENTS)


# Gets title from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_title")
@ensure_callback_message
async def edit_title(call: CallbackQuery, state: FSMContext) -> None:
    title = await state.get_value("title")
    await call.message.edit_text(  # type: ignore
        text='<b>Текущее название: <code>{}</code>\nВведите новое</b>'
        .format(title),
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
    await send_edit_event_message(message=message, state=state)


router.message(StepsForm.EDIT_GET_TITLE, F.text)(get_title(on_success_title))


# Gets date from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_date")
@ensure_callback_message
async def get_date_message(call: CallbackQuery, state: FSMContext) -> Any:
    if date := await state.get_value("date"):
        await call.message.edit_text(  # type: ignore
            text="Текущая дата: <code>{}</code>\n<b>Введите новую</b>"
            .format(normalize_datetime(date)),
            parse_mode="HTML",
        )
        return await state.set_state(StepsForm.EDIT_GET_DATE)
    logger.error("Could not get date from state")


async def on_success_date(message: Message, state: FSMContext) -> Any:
    await state.update_data(date=message.text)
    await message.answer(
        text="<b>Дата изменена ✅</b>",
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS)
    await send_edit_event_message(message=message, state=state)


router.message(StepsForm.EDIT_GET_DATE, F.text)(get_date(on_success_date))


# Gets text from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_text")
@ensure_callback_message
async def edit_text(call: CallbackQuery, state: FSMContext) -> None:
    text = await state.get_value("text")
    await call.message.edit_text(  # type: ignore
        text='<b>Текущий текст: <code>{}</code>\nВведите новый</b>'
        .format(text),
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
    await send_edit_event_message(message=message, state=state)


router.message(StepsForm.EDIT_GET_TEXT, F.text)(get_text(on_success_text))


# Gets mentions from user
@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_mentions")
@ensure_callback_message
async def edit_mentions(call: CallbackQuery, state: FSMContext, session: AsyncSession, redis: Redis) -> None:
    mentions = await state.get_value("mentions")
    await state.update_data(mentions="")
    users = await UserRepository(session, redis).get_users_in_group()
    await call.message.edit_text(  # type: ignore
        text='<b>Сейчас отмечены: {}\nКого отметить?</b>'
        .format(mentions),
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )
    await state.set_state(StepsForm.EDIT_GET_MENTIONS)


@ensure_callback_message
async def on_success_mentions(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(  # type: ignore
        text='<b>Упоминания изменены ✅</b>',
        parse_mode="HTML",
    )
    await send_edit_event_message(message=call.message, state=state)  # type: ignore


router.callback_query(StepsForm.EDIT_GET_MENTIONS)(get_mentions(on_success_mentions))


# Saves or doesn't save the event and sends start menu
@ensure_callback_message
async def on_event_save_confirmation(
        call: CallbackQuery,
        session: AsyncSession,
        state: FSMContext,
        redis: Redis,
        scheduler: AsyncIOScheduler
) -> Any:
    data = await state.get_data()
    event = EventsModel().model_validate({**data, "user_id": call.from_user.id})
    await EventRepository(session, redis, scheduler).update(event)
    await call.message.edit_text(  # type: ignore
        text="<b>Событие обновлено ✅</b>",
        parse_mode="HTML",
    )
    await send_events_list(call, session, redis)


@ensure_callback_message
async def on_event_save_cancellation(call: CallbackQuery, session: AsyncSession, redis: Redis) -> Any:
    await call.message.edit_text(  # type: ignore
        text="<b>Действие отменено ❌</b>",
        parse_mode="HTML",
    )
    await send_events_list(call, session, redis)


router.callback_query(StepsForm.EDIT_EVENTS, F.data == "confirm")(
    handle_event_update(on_event_save_confirmation, on_event_save_cancellation))
router.callback_query(StepsForm.EDIT_EVENTS, F.data == "cancel")(
    handle_event_update(on_event_save_confirmation, on_event_save_cancellation))


# Handle event callback to edit
@ensure_callback_message
async def edit_event(call: CallbackQuery, state: FSMContext, session: AsyncSession, redis: Redis) -> Any:
    if call.data and (data := await EventRepository(session, redis).get(uuid.UUID(call.data[1:]))):
        await state.update_data({k: str(v) for k, v in data.model_dump().items()})
        return await call.message.edit_text(  # type: ignore
            text="<b>Что изменить?</b>",
            parse_mode="HTML",
            reply_markup=inline.edit_events,
        )
    logger.error("Could not get event from callback data")

router.callback_query(StepsForm.EDIT_EVENTS)(process_events(edit_event))
