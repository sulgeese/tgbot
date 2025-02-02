from datetime import datetime
from typing import Any

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboard import inline
from bot.states import StepsForm
from db.redis_instance import redis
from db.repositories.user import UserRepository
from utils import format_datetime
from .utils import get_date, get_title, get_text, get_mentions, handle_event_update

router = Router()


# Entrypoint to start creating
@router.callback_query(F.data == "create_events")
async def send_title_message(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(
        text='<b>Введите название</b>',
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_TITLE)


# Gets title from user
async def on_success_title(message: Message, state: FSMContext) -> Any:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Введите дату отправки уведомления</b>\n(Пример:  <b>{}</b>)"
        .format(format_datetime(datetime.now())),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_DATE)


router.message(StepsForm.GET_TITLE, F.text)(get_title(on_success=on_success_title))


# Gets date from user
async def on_success_date(message: Message, state: FSMContext):
    await state.update_data(date=message.text)
    await message.answer(
        text='<b>Введите текст уведомления</b>',
        parse_mode="HTML",
    )
    return await state.set_state(StepsForm.GET_TEXT)


router.message(StepsForm.GET_DATE, F.text)(get_date(on_success_date))


# Gets text from user
async def on_success_text(message: Message, state: FSMContext, session: AsyncSession) -> Any:
    await state.update_data(text=message.text, mentions="")
    users = await UserRepository(session, redis).get_users_in_group()
    await message.answer(
        text='<b>Кого отметить?</b>',
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )
    await state.set_state(StepsForm.GET_MENTIONS)


router.message(StepsForm.GET_TEXT, F.text)(get_text(on_success_text))


# Display a message if user enters something other than text
@router.message(StepsForm.GET_TEXT)
@router.message(StepsForm.GET_TITLE)
@router.message(StepsForm.GET_DATE)
async def incorrect_message_type(message: Message) -> None:
    await message.answer(
        text='<b>Неверный формат. Попробуйте снова</b>\n',
        parse_mode="HTML",
    )


# Gets mentions from user
async def on_success_mention(call: CallbackQuery, state: FSMContext) -> Any:
    await state.set_state(StepsForm.WAITING_CONFIRM)
    return await call.message.edit_text(
        text='<b>Запланировать уведомление?</b>',
        parse_mode="HTML",
        reply_markup=inline.confirm,
    )


router.callback_query(StepsForm.GET_MENTIONS)(get_mentions(on_success_mention))


# Saves or doesn't save the event and sends start menu
async def on_event_save_confirmation(call: CallbackQuery) -> Any:
    await call.message.edit_text(
        text="<b>Событие добавлено ✅</b>",
        parse_mode="HTML",
    )


async def on_event_save_cancellation(call: CallbackQuery) -> Any:
    await call.message.edit_text(
        text="<b>Действие отменено ❌</b>",
        parse_mode="HTML",
    )


router.callback_query(StepsForm.WAITING_CONFIRM)(
    handle_event_update(on_event_save_confirmation, on_event_save_cancellation))
