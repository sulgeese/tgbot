from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from sqlalchemy.ext.asyncio import AsyncSession

from bot.filters.date import DateFilter, DateNotPassed
from bot.utils.statesform import StepsForm
from bot.utils.convert import datetime_to_str, str_to_datetime
from bot.utils.entities import entities_to_str, str_to_entities
from bot.templates.privateTMPL import *
from bot.keyboard.inline import confirmation
from bot.keyboard.reply import cancel_keyboard
from bot.handlers.apsched import send_message_by_date
from bot.db.requests import insert_event

from datetime import datetime, timedelta


pr_router = Router()
pr_router.message.filter(F.chat.type == "private")
pr_router.chat_member.filter(F.chat.type == "private")
pr_router.callback_query.filter(F.message.chat.type == "private")


@pr_router.message(Command('create_event'))
async def create_announcement_command(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=enter_date.format(datetime_to_str(datetime.now())),
        parse_mode='HTML',
        reply_markup=cancel_keyboard)
    await state.set_state(StepsForm.GET_DATE)


# Нажатие на кнопку
@pr_router.message(StepsForm.GET_TEXT, F.text == 'Отмена')
@pr_router.message(StepsForm.GET_DATE, F.text == 'Отмена')
async def go_back_i_want_to_be_monkey(message: Message, state: FSMContext):
    await message.delete()
    await message.answer(
        text=cancel_command,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove())
    await state.clear()


# Колбеки
@pr_router.callback_query(F.data == 'cancel')
async def cancel_call(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer(
        text=cancel_command,
        parse_mode='HTML')
    await state.clear()


@pr_router.callback_query(F.data == 'confirm')
async def confirm_call(call: CallbackQuery, state: FSMContext, scheduler: AsyncIOScheduler, session: AsyncSession):
    await call.message.delete()
    data = await state.get_data()
    scheduler.add_job(
        send_message_by_date,
        trigger='date',
        run_date=max(str_to_datetime(data['date']), datetime.now() + timedelta(seconds=5)),
        kwargs={'text': data['text'], 'entities': data['entities']})
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
@pr_router.message(StepsForm.GET_DATE, DateFilter(), DateNotPassed())
async def get_date(message: Message, state: FSMContext):
    await state.set_state(StepsForm.GET_TEXT)
    await state.update_data(date=message.text)
    await message.answer(
        text=enter_text.format(message.text),
        parse_mode='HTML')


@pr_router.message(StepsForm.GET_DATE, DateFilter())
async def get_date_inc(message: Message):
    await message.answer(
        text=incorrect_date,
        parse_mode='HTML')


@pr_router.message(StepsForm.GET_DATE)
async def get_date_incf(message: Message):
    await message.answer(
        text=incorrect_date_format.format(datetime_to_str(datetime.now())),
        parse_mode='HTML')


# Текст
@pr_router.message(StepsForm.GET_TEXT, F.text)
async def get_text(message: Message, state: FSMContext):
    await state.update_data(text=message.text, entities=entities_to_str(message.entities))
    data = await state.get_data()
    await state.set_state(StepsForm.WAITING_CONFIRM)
    await message.answer(
        text=final_message,
        entities=str_to_entities(data['entities']),
        parse_mode='HTML',
        reply_markup=confirmation)


@pr_router.message(StepsForm.GET_TEXT)
async def get_text_inc(message: Message):
    await message.answer(
        text=incorrect_text,
        parse_mode='HTML')
