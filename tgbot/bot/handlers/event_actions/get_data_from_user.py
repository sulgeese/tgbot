import inspect
from datetime import datetime
from typing import Any, Callable

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.keyboard import inline
from db import requests
from utils import parse_datetime, format_datetime


def push_arguments(on_success_func: Callable[..., Any]):
    async def _push_arguments(*args, **kwargs) -> Any:
        kw_arguments = {
            name: parameter for name, parameter in kwargs.items()
            if name in inspect.signature(on_success_func).parameters
        }
        return await on_success_func(*args, **kw_arguments)

    return _push_arguments


def get_title(on_success_func: Callable[..., Any]):
    async def _get_title(*args, **kwargs) -> Any:
        return await push_arguments(on_success_func)(*args, **kwargs)

    async def wrapper(*args, **kwargs):
        return await _get_title(*args, **kwargs)

    return wrapper


def get_date(on_success_func: Callable[..., Any]):
    async def _get_date(message: Message, *args, **kwargs) -> Any:
        if input_date := parse_datetime(message.text):
            if input_date >= datetime.now():
                return await push_arguments(on_success_func)(message, *args, **kwargs)
            return await message.answer(
                text='<b>Эта дата уже прошла. Попробуйте снова</b>',
                parse_mode="HTML",
            )
        return await message.answer(
            text='<b>Неправильный формат. Попробуйте снова</b>\n(Пример текущей даты: <b>{}</b>)\n'
            .format(format_datetime(datetime.now())),
            parse_mode="HTML",
        )

    async def wrapper(*args, **kwargs):
        return await _get_date(*args, **kwargs)

    return wrapper


def get_text(on_success_func: Callable[..., Any]):
    async def _get_text(*args, **kwargs) -> Any:
        return await push_arguments(on_success_func)(*args, **kwargs)

    async def wrapper(*args, **kwargs):
        return await _get_text(*args, **kwargs)

    return wrapper


def get_mentions(on_success_func: Callable[..., Any]):
    async def _get_mentions(call: CallbackQuery, *args, state: FSMContext, session: AsyncSession, **kwargs) -> Any:
        print(call.data)
        if call.data == "confirm_mentions":
            return await push_arguments(on_success_func)(call, *args, state=state, **kwargs)
        if call.data.startswith("@"):
            data = await state.get_data()
            users = await requests.get_users_in_group(session)
            mentions = data.get("mentions", "")
            if call.data.count("@") >= 2:
                mentions = ""
            if call.data not in mentions:
                mentions += f" {call.data}"
            await state.update_data(mentions=mentions.strip())
            return await call.message.edit_text(
                text=f"<b>Кого отметить?\nОтмечены {mentions}</b>",
                parse_mode="HTML",
                reply_markup=inline.get_users_keyboard(users, mentions),
            )
        if call.data == "cancel_mentions":
            await state.update_data(mentions="")
            users = await requests.get_users_in_group(session)
            return await call.message.edit_text(
                text='<b>Кого отметить?</b>',
                parse_mode="HTML",
                reply_markup=inline.get_users_keyboard(users),
            )

    async def wrapper(*args, **kwargs):
        return await _get_mentions(*args, **kwargs)

    return wrapper
