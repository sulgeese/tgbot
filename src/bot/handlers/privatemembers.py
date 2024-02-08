from datetime import timedelta, datetime

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.ext.asyncio import AsyncSession

from src.bot.filters.date import DateNotPassed, DateFilter
from src.bot.filters.user import UserInGroup
from src.bot.handlers.apsched import send_message_by_date
from src.bot.keyboard import inline, reply
from src.bot.states import StepsForm
from src.bot.utils.entities import entities_to_str, str_to_entities
from src.db.requests import insert_event, get_users_in_group
from src.utils import datetime_to_str, str_to_datetime

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


@pr_members_router.message(F.text == "📆 События")
async def events_inline(message: Message) -> None:
    await message.delete()
    await message.answer(
        text='<b>Что хотите сделать?</b>',
        reply_markup=inline.events,
        parse_mode="HTML"
    )


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
        text='<b>Введите дату отправки оповещения:</b>\n' \
             '(Пример:  <b>{}</b>)'
        .format(datetime_to_str(datetime.now())),
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_DATE)


@pr_members_router.message(StepsForm.GET_DATE, DateFilter(), DateNotPassed())
async def get_text_message(message: Message, state: FSMContext) -> None:
    await state.update_data(date=message.text)
    await message.answer(
        text='<b>Введите текст оповещения:</b>\n',
        parse_mode="HTML",
    )
    await state.set_state(StepsForm.GET_TEXT)


@pr_members_router.message(StepsForm.GET_DATE, DateFilter())
async def get_date_inc(message: Message) -> None:
    await message.answer(
        text='<b>Эта дата уже прошла. Попробуйте снова:</b>',
        parse_mode="HTML")


@pr_members_router.message(StepsForm.GET_DATE)
async def get_date_incf(message: Message) -> None:
    await message.answer(
        text='<b>Неправильный формат. Попробуйте снова:</b>\n' \
             '(Пример текущей даты: <b>{}</b>)\n'
        .format(datetime_to_str(datetime.now())),
        parse_mode="HTML")


@pr_members_router.message(StepsForm.GET_TEXT, F.text)
async def get_text(message: Message, state: FSMContext, session: AsyncSession) -> None:
    await state.update_data(text=message.text, entities=entities_to_str(message.entities))
    users = await get_users_in_group(session)
    await message.answer(
        text='<b>Кого отметить?</b>',
        parse_mode="HTML",
        reply_markup=inline.get_users(users),
    )
    await state.set_state(StepsForm.GET_MENTION)


@pr_members_router.message(StepsForm.GET_MENTION, F.text)
async def get_text(message: Message, state: FSMContext) -> None:
    await state.update_data(mention=message.text)
    await message.answer(
        text='<b>Запланировать оповещение?</b>',
        parse_mode="HTML",
        reply_markup=inline.confirm)
    await state.set_state(StepsForm.WAITING_CONFIRM)


@pr_members_router.message(StepsForm.GET_TEXT)
async def get_text_inc(message: Message) -> None:
    await message.answer(
        text='<b>Неверный формат. Попробуйте снова:</b>\n',
        parse_mode="HTML")


@pr_members_router.callback_query(F.data == "confirm")
async def confirm_call(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler,
                       session: AsyncSession) -> None:
    await call.message.delete()
    data = await state.get_data()
    scheduler.add_job(
        send_message_by_date,
        trigger="date",
        run_date=max(str_to_datetime(data["date"]), datetime.now() + timedelta(seconds=10)),
        kwargs={"title": data["title"], "text": data["text"], "entities": data["entities"]}
    )
    await insert_event(
        session=session,
        # title=data["title"],
        date=str_to_datetime(data["date"]),
        text=data["text"],
        user_id=call.from_user.id,
    )
    await state.clear()
    await call.message.answer(
        text='<b>Уведомление добавлено в очередь</b>',
        parse_mode="HTML",
    )


@pr_members_router.callback_query(F.data == "cancel")
async def cancel_call(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()
    await call.message.answer(
        text='<b>Действие отменено</b>',
        parse_mode="HTML")
    await state.clear()


@pr_members_router.callback_query(F.data == "edit_events")
async def edit_events(call: CallbackQuery, state: FSMContext) -> None: ...


@pr_members_router.callback_query(F.data == "delete_events")
async def delete_events(call: CallbackQuery, state: FSMContext) -> None: ...


@pr_members_router.callback_query(F.data == "search_events")
async def search_events(call: CallbackQuery, state: FSMContext) -> None: ...
