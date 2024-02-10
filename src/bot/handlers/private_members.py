from datetime import timedelta, datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.date import DateNotPassed, DateFilter
from bot.filters.user import UserInGroup
from bot.handlers.bot_messages import send_message, send_events_list, send_edit_event_message, send_start_menu
from bot.keyboard import inline, reply
from bot.states import StepsForm
from db import requests
from utils import datetime_to_str, str_to_datetime

pr_members_router = Router()

pr_members_router.message.filter(F.chat.type == "private", UserInGroup())
pr_members_router.chat_member.filter(F.chat.type == "private", UserInGroup())
pr_members_router.callback_query.filter(F.message.chat.type == "private", UserInGroup())


@pr_members_router.message(Command("start"))
async def start_command(message: Message) -> None:
    await message.answer(
        text='Здарова',
        reply_markup=reply.start,
    )


@pr_members_router.callback_query(F.data == "back")
async def start_menu(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await call.message.edit_text(
        text='<b>Что хотите сделать?</b>',
        reply_markup=inline.events,
        parse_mode="HTML"
    )


@pr_members_router.message(F.text == "📆 События")
async def start_menu(message: Message, state: FSMContext) -> None:
    await send_start_menu(message=message, state=state)


@pr_members_router.callback_query(F.data == "edit_events")
async def edit_events(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    await send_events_list(call=call, session=session)
    await state.set_state(StepsForm.EDIT_EVENTS)


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS, F.data.startswith("$"))
async def edit_event(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await requests.select_event(session=session, event_id=int(call.data[1:]))
    await state.update_data(id=data["id"], title=data["title"], date=datetime_to_str(data["date"]), text=data["text"],
                            mentions=data["mentions"], event_id=call.data[1:])
    await call.message.edit_text(
        text="<b>Что изменить?</b>",
        parse_mode="HTML",
        reply_markup=inline.edit_events,
    )


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_date")
async def edit_date(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.delete()
    await call.message.answer(
        text="Текущая дата: <code>{}</code>\n<b>Введите новую</b>"
        .format(data["date"], datetime_to_str(datetime.now())),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS_DATE)


@pr_members_router.message(StepsForm.EDIT_EVENTS_DATE, DateFilter(), DateNotPassed())
async def edit_date_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text)
    await message.answer(
        text="<b>Дата изменена ✅</b>",
        parse_mode="HTML",
    )
    await send_edit_event_message(message=message, state=state)


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_title")
async def edit_title(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.delete()
    await call.message.answer(
        text='<b>Текущее название: <code>{}</code>\nВведите новое</b>'
        .format(data["title"]),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS_TITLE)


@pr_members_router.message(StepsForm.EDIT_EVENTS_TITLE)
async def edit_title_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Название изменено ✅</b>",
        parse_mode="HTML",
    )
    await send_edit_event_message(message=message, state=state)


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_text")
async def edit_text(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    await call.message.delete()
    await call.message.answer(
        text='<b>Текущий текст: <code>{}</code>\nВведите новый</b>'
        .format(data["text"]),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.EDIT_EVENTS_TEXT)


@pr_members_router.message(StepsForm.EDIT_EVENTS_TEXT)
async def edit_text_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text)
    await message.answer(
        text="<b>Текст уведомления изменён ✅</b>",
        parse_mode="HTML",
    )
    await send_edit_event_message(message=message, state=state)


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_mentions")
async def edit_mentions(call: CallbackQuery, state: FSMContext, session: AsyncSession) -> None:
    data = await state.get_data()
    await state.update_data(mentions="")
    await call.message.delete()
    users = await requests.get_users_in_group(session)
    await call.message.answer(
        text='<b>Сейчас отмечены: {}\nКого отметить?</b>'
        .format(data["mentions"]),
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )
    await state.set_state(StepsForm.EDIT_EVENTS_MENTIONS)


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS_MENTIONS, F.data == "confirm_mentions")
async def confirm_mentions(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()
    await call.message.answer(
        text='<b>Упоминания изменены ✅</b>',
        parse_mode="HTML",
        )
    await send_edit_event_message(message=call.message, state=state)


@pr_members_router.message(StepsForm.EDIT_EVENTS_MENTIONS)
async def edit_mentions_confirm(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Текст уведомления изменён ✅</b>",
        parse_mode="HTML",
    )
    await send_edit_event_message(message=message, state=state)


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS, F.data == "edit_confirm")
async def edit_event_confirm(call: CallbackQuery, state: FSMContext, session: AsyncSession, scheduler: AsyncIOScheduler):
    data = await state.get_data()
    title, date, text, mentions, event_id = (data.get("title", None), str_to_datetime(data.get("date", None)),
                                             data.get("text", None), data.get("mentions", None), data.get("event_id", None))
    await requests.edit_event(
        session=session,
        title=title,
        date=date,
        text=text,
        mentions=mentions,
        event_id=int(event_id),
        scheduler=scheduler
    )
    scheduler.add_job(
        id=str(event_id),
        func=send_message,
        trigger="date",
        run_date=max(date, datetime.now() + timedelta(seconds=10)),
        kwargs={"title": title, "text": text, "mentions": mentions}
    )
    await send_start_menu(message=call.message, state=state)


@pr_members_router.callback_query(F.data == "create_events")
async def get_title_message(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()
    await call.message.answer(
        text='<b>Введите название</b>',
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_TITLE)


@pr_members_router.message(StepsForm.GET_TITLE)
async def get_date_message(message: Message, state: FSMContext) -> None:
    await state.update_data(title=message.text)
    await message.answer(
        text="<b>Введите дату отправки уведомления</b>\n(Пример:  <b>{}</b>)"
        .format(datetime_to_str(datetime.now())),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_DATE)


@pr_members_router.message(StepsForm.GET_DATE, DateFilter(), DateNotPassed())
async def get_text_message(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text)
    await message.answer(
        text='<b>Введите текст уведомления</b>',
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_TEXT)


@pr_members_router.message(StepsForm.EDIT_EVENTS_DATE, DateFilter())
@pr_members_router.message(StepsForm.GET_DATE, DateFilter())
async def get_date_inc(message: Message) -> None:
    await message.answer(
        text='<b>Эта дата уже прошла. Попробуйте снова</b>',
        parse_mode="HTML")


@pr_members_router.message(StepsForm.EDIT_EVENTS_DATE)
@pr_members_router.message(StepsForm.GET_DATE)
async def get_date_incf(message: Message) -> None:
    await message.answer(
        text='<b>Неправильный формат. Попробуйте снова</b>\n' \
             '(Пример текущей даты: <b>{}</b>)\n'
        .format(datetime_to_str(datetime.now())),
        parse_mode="HTML")


@pr_members_router.message(StepsForm.GET_TEXT, F.text)
async def get_text(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(text=message.text)
    users = await requests.get_users_in_group(session)
    await message.answer(
        text='<b>Кого отметить?</b>',
        parse_mode="HTML",
        reply_markup=inline.get_users_keyboard(users),
    )
    await state.set_state(StepsForm.GET_MENTION)


@pr_members_router.callback_query(StepsForm.EDIT_EVENTS_MENTIONS, F.data.startswith("@"))
@pr_members_router.callback_query(StepsForm.GET_MENTION, F.data.startswith("@"))
async def get_mention(call: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()
    mentions = data.get("mentions", '')
    if call.data.count("@") >= 2:
        mentions = ""
    if call.data not in mentions:
        mentions += f" {call.data}"
    await state.update_data(mentions=mentions.strip())


@pr_members_router.callback_query(StepsForm.GET_MENTION, F.data == "confirm_mentions")
async def confirm_mentions(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()
    await call.message.answer(
        text='<b>Запланировать уведомление?</b>',
        parse_mode="HTML",
        reply_markup=inline.confirm)
    await state.set_state(StepsForm.WAITING_CONFIRM)


@pr_members_router.message(StepsForm.GET_TEXT)
async def get_text_inc(message: Message) -> None:
    await message.answer(
        text='<b>Неверный формат. Попробуйте снова</b>\n',
        parse_mode="HTML")


@pr_members_router.callback_query(F.data == "confirm_creation")
async def confirm_creation(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler,
                           session: AsyncSession) -> None:
    data = await state.get_data()
    title, date, text, mentions = (data.get("title", None), str_to_datetime(data.get("date", None)),
                                   data.get("text", None), data.get("mentions", None))
    await requests.insert_event(
        session=session,
        title=title,
        date=date,
        text=text,
        mentions=mentions,
        user_id=call.from_user.id,
    )
    event_id = await requests.get_event_id(session=session, title=title)
    scheduler.add_job(
        id=str(event_id),
        func=send_message,
        trigger="date",
        run_date=max(date, datetime.now() + timedelta(seconds=10)),
        kwargs={"title": title, "text": text, "mentions": mentions}
    )
    await call.message.edit_text(
        text='<b>Уведомление добавлено ✅</b>',
        parse_mode="HTML",
    )
    await send_start_menu(message=call.message, state=state)


@pr_members_router.callback_query(F.data == "cancel_creation")
async def cancel_creation(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()
    await call.message.answer(
        text='<b>Действие отменено ❌</b>',
        parse_mode="HTML")
    await state.clear()


@pr_members_router.callback_query(F.data == "delete_events")
async def delete_events(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await send_events_list(call=call, session=session)
    await state.set_state(StepsForm.DELETE_EVENTS)


@pr_members_router.callback_query(F.data.startswith("$"), StepsForm.DELETE_EVENTS)
async def delete_events(call: CallbackQuery, session: AsyncSession, scheduler: AsyncIOScheduler) -> None:
    event_id = call.data[1:]
    await requests.delete_event(session=session, scheduler=scheduler, event_id=int(event_id))
    await send_events_list(call=call, session=session)


@pr_members_router.callback_query(F.data == "cancel_event")
@pr_members_router.callback_query(F.data == "search_events")
async def search_events(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    await send_events_list(call=call, session=session)
    await state.set_state(StepsForm.SEARCH_EVENTS)


@pr_members_router.callback_query(F.data.startswith("$"), StepsForm.SEARCH_EVENTS)
async def search_events(call: CallbackQuery, session: AsyncSession, state: FSMContext) -> None:
    event = await requests.select_event(session=session, event_id=int(call.data[1:]))
    await call.message.edit_text(
        text=f"<i><b>{event['title']}</b></i>\n{event['text']}\n{event['mentions']}\n\nДата: {datetime_to_str(event['date'])}",
        reply_markup=inline.cancel_event,
        parse_mode="HTML",
    )
