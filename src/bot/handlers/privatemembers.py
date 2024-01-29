from datetime import timedelta, datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.ext.asyncio import AsyncSession

from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardRemove, CallbackQuery, Message
from aiogram import Router, F

from src.bot.templates.privateTMPL import *
from src.bot.handlers.apsched import send_message_by_date
from src.bot.keyboard.inline import confirmation
from src.bot.keyboard.reply import cancel_keyboard, webapp_keyboard
from src.bot.utils.entities import entities_to_str, str_to_entities
from src.utils import datetime_to_str, str_to_datetime
from src.bot.filters.date import DateNotPassed, DateFilter
from src.bot.filters.user import UserInGroup
from src.db.requests import insert_event
from src.bot.states import StepsForm


pr_members_router = Router()

pr_members_router.message.filter(F.chat.type == "private", UserInGroup())
pr_members_router.chat_member.filter(F.chat.type == "private", UserInGroup())
pr_members_router.callback_query.filter(F.message.chat.type == "private", UserInGroup())


@pr_members_router.message(Command('start'))
async def start_command(message: Message) -> None:
    await message.answer(
        text=start,
        reply_markup=webapp_keyboard,
    )


@pr_members_router.message(Command('create_event'))
async def create_event_command(message: Message, state: FSMContext) -> None:
    await message.delete()
    await message.answer(
        text=enter_date.format(datetime_to_str(datetime.now())),
        parse_mode='HTML',
        reply_markup=cancel_keyboard)
    await state.set_state(StepsForm.GET_DATE)


# Нажатие на кнопку
@pr_members_router.message(StepsForm.GET_TEXT, F.text == 'Отмена')
@pr_members_router.message(StepsForm.GET_DATE, F.text == 'Отмена')
async def go_back_i_want_to_be_monkey(message: Message, state: FSMContext) -> None:
    await message.delete()
    await message.answer(
        text=cancel_command,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove())
    await state.clear()


# Колбеки
@pr_members_router.callback_query(F.data == 'cancel')
async def cancel_call(call: CallbackQuery, state: FSMContext) -> None:
    await call.message.delete()
    await call.message.answer(
        text=cancel_command,
        parse_mode='HTML')
    await state.clear()


@pr_members_router.callback_query(F.data == 'confirm')
async def confirm_call(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler, session: AsyncSession) -> None:
    await call.message.delete()
    data = await state.get_data()
    scheduler.add_job(
        send_message_by_date,
        trigger='date',
        run_date=max(str_to_datetime(data['date']), datetime.now() + timedelta(seconds=5)),
        kwargs={'text': data['text'], 'entities': data['entities']}
    )
    await insert_event(
        session=session,
        date=str_to_datetime(data['date']),
        text=data['text'],
        user_id=call.from_user.id,
    )
    await state.clear()
    await call.message.answer(
        text=event_added,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove())


# Дата
@pr_members_router.message(StepsForm.GET_DATE, DateFilter(), DateNotPassed())
async def get_date(message: Message, state: FSMContext) -> None:
    await state.set_state(StepsForm.GET_TEXT)
    await state.update_data(date=message.text)
    await message.answer(
        text=enter_text.format(message.text),
        parse_mode='HTML')


@pr_members_router.message(StepsForm.GET_DATE, DateFilter())
async def get_date_inc(message: Message) -> None:
    await message.answer(
        text=incorrect_date,
        parse_mode='HTML')


@pr_members_router.message(StepsForm.GET_DATE)
async def get_date_incf(message: Message) -> None:
    await message.answer(
        text=incorrect_date_format.format(datetime_to_str(datetime.now())),
        parse_mode='HTML')


# Текст
@pr_members_router.message(StepsForm.GET_TEXT, F.text)
async def get_text(message: Message, state: FSMContext) -> None:
    await state.update_data(text=message.text, entities=entities_to_str(message.entities))
    data = await state.get_data()
    await state.set_state(StepsForm.WAITING_CONFIRM)
    await message.answer(
        text=final_message,
        entities=str_to_entities(data['entities']),
        parse_mode='HTML',
        reply_markup=confirmation)


@pr_members_router.message(StepsForm.GET_TEXT)
async def get_text_inc(message: Message) -> None:
    await message.answer(
        text=incorrect_text,
        parse_mode='HTML')
