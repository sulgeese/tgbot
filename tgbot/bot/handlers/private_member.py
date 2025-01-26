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
from utils import datetime_to_str

router = Router()

router.message.filter(F.chat.type == "private", UserInGroup())
router.chat_member.filter(F.chat.type == "private", UserInGroup())
router.callback_query.filter(F.message.chat.type == "private", UserInGroup())


@router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer(
        text="Здарова",
        reply_markup=reply.start,
    )


@router.callback_query(F.data == "back")
async def start_menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(
        text="<b>Что хотите сделать?</b>",
        reply_markup=inline.events,
        parse_mode="HTML"
    )


@router.message(F.text == "📆 События")
async def start_menu_new(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.delete()
    await message.answer(
        text='<b>Что хотите сделать?</b>',
        reply_markup=inline.events,
        parse_mode="HTML"
    )


@router.callback_query(F.data == "edit_events")
async def edit_events(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.EDIT_EVENTS)


@router.callback_query(StepsForm.EDIT_EVENTS, F.data.startswith("$"))
async def edit_event(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await requests.select_event(session=session, event_id=int(call.data[1:]))
    await state.update_data(**data)
    await call.message.edit_text(
        text="<b>Что изменить?</b>",
        parse_mode="HTML",
        reply_markup=inline.edit_events,
    )


@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_date")
async def edit_date(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.edit_text(
        text="Текущая дата: <code>{}</code>\n<b>Введите новую</b>"
        .format(data["date"], datetime_to_str(datetime.now())),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS_DATE)


@router.message(StepsForm.EDIT_EVENTS_DATE, DateFilter(), DateNotPassed())
async def edit_date_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text)
    await message.answer(
        text="<b>Дата изменена ✅</b>",
        parse_mode="HTML",
    )
    await bot_messages.send_edit_event_message(message=message, state=state)


@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_title")
async def edit_title(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.edit_text(
        text='<b>Текущее название: <code>{}</code>\nВведите новое</b>'
        .format(data["title"]),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS_TITLE)


@router.message(StepsForm.EDIT_EVENTS_TITLE)
async def edit_title_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Название изменено ✅</b>",
        parse_mode="HTML",
    )
    await bot_messages.send_edit_event_message(message=message, state=state)


@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_text")
async def edit_text(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.edit_text(
        text='<b>Текущий текст: <code>{}</code>\nВведите новый</b>'
        .format(data["text"]),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS_TEXT)


@router.message(StepsForm.EDIT_EVENTS_TEXT)
async def edit_text_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await message.answer(
        text="<b>Текст уведомления изменён ✅</b>",
        parse_mode="HTML",
    )
    await bot_messages.send_edit_event_message(message=message, state=state)


@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_mentions")
async def edit_mentions(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    await state.update_data(mentions="")
    users = await requests.get_users_in_group(session)
    await call.message.edit_text(
        text='<b>Сейчас отмечены: {}\nКого отметить?</b>'
        .format(data["mentions"]),
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )
    await state.set_state(StepsForm.EDIT_EVENTS_MENTIONS)


@router.callback_query(StepsForm.EDIT_EVENTS_MENTIONS, F.data == "confirm_mentions")
async def confirm_mentions(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        text='<b>Упоминания изменены ✅</b>',
        parse_mode="HTML",
    )
    await bot_messages.send_edit_event_message(message=call.message, state=state)


@router.message(StepsForm.EDIT_EVENTS_MENTIONS)
async def edit_mentions_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Текст уведомления изменён ✅</b>",
        parse_mode="HTML",
    )
    await bot_messages.send_edit_event_message(message=message, state=state)


@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_confirm")
async def edit_event_confirm(call: CallbackQuery, state: FSMContext, session: AsyncSession,
                             scheduler: AsyncIOScheduler):
    await bot_messages.update_event(call=call, state=state, session=session, scheduler=scheduler)
    await bot_messages.send_start_menu(call=call, state=state)


@router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_cancel")
async def edit_event_confirm(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await bot_messages.send_start_menu(call=call, state=state)


@router.callback_query(F.data == "create_events")
async def get_title_message(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        text='<b>Введите название</b>',
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_TITLE)


@router.message(StepsForm.GET_TITLE)
async def get_date_message(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Введите дату отправки уведомления</b>\n(Пример:  <b>{}</b>)"
        .format(datetime_to_str(datetime.now())),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_DATE)


@router.message(StepsForm.GET_DATE, DateFilter(), DateNotPassed())
async def get_text_message(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text)
    await message.answer(
        text='<b>Введите текст уведомления</b>',
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_TEXT)


@router.message(StepsForm.EDIT_EVENTS_DATE, DateFilter())
@router.message(StepsForm.GET_DATE, DateFilter())
async def get_date_inc(message: Message) -> None:
    await message.answer(
        text='<b>Эта дата уже прошла. Попробуйте снова</b>',
        parse_mode="HTML")


@router.message(StepsForm.EDIT_EVENTS_DATE)
@router.message(StepsForm.GET_DATE)
async def get_date_incf(message: Message) -> None:
    await message.answer(
        text='<b>Неправильный формат. Попробуйте снова</b>\n(Пример текущей даты: <b>{}</b>)\n'
        .format(datetime_to_str(datetime.now())),
        parse_mode="HTML")


@router.message(StepsForm.GET_TEXT, F.text)
async def get_text(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(text=message.text, mentions="")
    users = await requests.get_users_in_group(session)
    await message.answer(
        text='<b>Кого отметить?</b>',
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )
    await state.set_state(StepsForm.GET_MENTION)


@router.callback_query(F.data == "cancel_mentions")
async def cancel_mentions(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(mentions="")
    users = await requests.get_users_in_group(session)
    await call.message.edit_text(
        text='<b>Кого отметить?</b>',
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )


@router.callback_query(StepsForm.EDIT_EVENTS_MENTIONS, F.data.startswith("@"))
@router.callback_query(StepsForm.GET_MENTION, F.data.startswith("@"))
async def get_mention(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    users = await requests.get_users_in_group(session)
    mentions = data.get("mentions", "")
    if call.data.count("@") >= 2:
        mentions = ""
    if call.data not in mentions:
        mentions += f" {call.data}"
    await state.update_data(mentions=mentions.strip())
    await call.message.edit_text(
        text=f"<b>Кого отметить?\nОтмечены {mentions}</b>",
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users, mentions),
    )


@router.callback_query(StepsForm.GET_MENTION, F.data == "confirm_mentions")
async def confirm_mentions(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        text='<b>Запланировать уведомление?</b>',
        parse_mode="HTML",
        reply_markup=inline.confirm)
    await state.set_state(StepsForm.WAITING_CONFIRM)


@router.message(StepsForm.GET_TEXT)
async def get_text_inc(message: Message) -> None:
    await message.answer(
        text='<b>Неверный формат. Попробуйте снова</b>\n',
        parse_mode="HTML")


@router.callback_query(F.data == "confirm_creation")
async def confirm_creation(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler,
                           session: AsyncSession) -> None:
    await bot_messages.update_event(call=call, state=state, session=session, scheduler=scheduler)
    await call.message.edit_text(
        text='<b>Уведомление добавлено ✅</b>',
        parse_mode="HTML",
    )
    await bot_messages.send_start_menu(call=call, state=state)


@router.callback_query(F.data == "cancel_creation")
async def cancel_creation(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.edit_text(
        text='<b>Действие отменено ❌</b>',
        parse_mode="HTML")
    await state.clear()


@router.callback_query(F.data == "delete_events")
async def delete_event_list(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.DELETE_EVENTS)


@router.callback_query(F.data.startswith("$"), StepsForm.DELETE_EVENTS)
async def delete_event(call: CallbackQuery, session: AsyncSession, scheduler: AsyncIOScheduler) -> None:
    await requests.delete_event(session=session, scheduler=scheduler, event_id=int(call.data[1:]))
    await bot_messages.send_events_list(call=call, session=session)


@router.callback_query(F.data == "cancel_event")
@router.callback_query(F.data == "search_events")
async def search_events(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await bot_messages.send_events_list(call=call, session=session)
    await state.set_state(StepsForm.SEARCH_EVENTS)


@router.callback_query(F.data.startswith("$"), StepsForm.SEARCH_EVENTS)
async def search_events(call: CallbackQuery, session: AsyncSession) -> None:
    data = await requests.select_event(session=session, event_id=int(call.data[1:]))
    title, text, mentions, date = data.get("title"), data.get("text"), data.get("mentions"), data.get("date")
    await call.message.edit_text(
        text=f"<i><b>{title}</b></i>\n{text}\n{mentions}\n\nБудет отправлено в {date}",
        reply_markup=inline.cancel_event,
        parse_mode="HTML",
    )
