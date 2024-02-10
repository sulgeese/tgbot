from datetime import datetime, timedelta

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboard import inline
from bot.states import StepsForm
from db.requests import select_current_users_events, insert_event, get_event_id
from settings import settings
from utils import str_to_datetime


async def send_message(bot: Bot, title: str, text: str, mentions: str) -> None:
    await bot.send_message(chat_id=settings.bots.supergroup_id,
                           text=f"""<i><b>{title}</b></i>
                           {text}
                           {mentions}""",
                           message_thread_id=settings.bots.theme_id,
                           parse_mode="HTML",
                           )


async def send_events_list(call: CallbackQuery, session: AsyncSession):
    data = await select_current_users_events(session=session, user_id=call.from_user.id)
    await call.message.edit_text(
        text="<b>Уведомления</b>",
        parse_mode="HTML",
        reply_markup=inline.get_events_keyboard(data)
    )


async def send_edit_event_message(message: Message, state: FSMContext) -> None:
    await message.answer(
        text="<b>Что изменить?</b>",
        parse_mode="HTML",
        reply_markup=inline.edit_events,
    )
    await state.set_state(StepsForm.EDIT_EVENTS)


async def send_start_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.delete()
    await message.answer(
        text='<b>Что хотите сделать?</b>',
        reply_markup=inline.events,
        parse_mode="HTML"
    )


# async def add_event(call: CallbackQuery, state: FSMContext, session: AsyncSession, scheduler: AsyncIOScheduler):
#     data = await state.get_data()
#     title, date, text, mentions = (data.get("title", None), str_to_datetime(data.get("date", None)),
#                                    data.get("text", None), data.get("mentions", None))
#     await insert_event(
#         session=session,
#         title=title,
#         date=date,
#         text=text,
#         mentions=mentions,
#         user_id=call.from_user.id,
#     )
#     event_id = await get_event_id(session=session, title=title)
#     scheduler.add_job(
#         id=str(event_id),
#         func=send_message,
#         trigger="date",
#         run_date=max(date, datetime.now() + timedelta(seconds=10)),
#         kwargs={"title": title, "text": text, "mentions": mentions}
#     )
#     await state.clear()
