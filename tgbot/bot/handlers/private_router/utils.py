import inspect
from datetime import datetime
from typing import Any, Callable, Awaitable

from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from redis.asyncio import Redis
from sqlmodel.ext.asyncio.session import AsyncSession

from bot.handlers.utils import send_start_menu
from bot.keyboards import inline
from db.repositories import UserRepository
from bot.datetime_utils import parse_datetime, format_datetime


def push_arguments(perform: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    """
    Helper for dynamically filtering arguments to match a callback's signature.

    :param perform: A callable that will be dynamically invoked
        with the filtered arguments.
    :type perform: Callable[..., Any]
    :return: An asynchronous function ready to invoke the provided callback
        with the filtered arguments.
    :rtype: Callable[..., Awaitable[Any]]
    """

    async def _push_arguments(*args: Any, **kwargs: Any) -> Any:
        kw_arguments = {
            name: parameter for name, parameter in kwargs.items()
            if name in inspect.signature(perform).parameters
        }
        return await perform(*args, **kw_arguments)

    return _push_arguments


def get_title(on_success: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    async def _get_title(*args: Any, **kwargs: Any) -> Any:
        return await push_arguments(on_success)(*args, **kwargs)

    return _get_title


def get_date(on_success: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    async def _get_date(message: Message, *args: Any, **kwargs: Any) -> Any:
        if input_date := parse_datetime(message.text):
            if input_date >= datetime.now():
                return await push_arguments(on_success)(message, *args, **kwargs)
            return await message.answer(
                text="<b>Эта дата уже прошла. Попробуйте снова</b>",
                parse_mode="HTML",
            )
        return await message.answer(
            text="<b>Неправильный формат. Попробуйте снова</b>\n(Пример текущей даты: <b>{}</b>)\n"
            .format(format_datetime(datetime.now())),
            parse_mode="HTML",
        )

    return _get_date


def get_text(on_success: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    async def _get_text(*args: Any, **kwargs: Any) -> Any:
        return await push_arguments(on_success)(*args, **kwargs)

    return _get_text


def get_mentions(on_success: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    async def _get_mentions(
            call: CallbackQuery,
            *args: Any,
            state: FSMContext,
            session: AsyncSession,
            redis: Redis,
            **kwargs: Any
    ) -> Any:
        if call.data == "confirm_mentions":
            return await push_arguments(on_success)(call, *args, state=state, session=session, redis=redis, **kwargs)

        users = await UserRepository(session, redis).get_users_in_group()
        if call.data and call.data.startswith("@"):
            if call.data == "@all" and users:
                mentions =" ".join(map(lambda user: f"@{user.username}", users))
            else:
                mentions = await state.get_value("mentions", default="")
                if call.data not in mentions:
                    mentions += f" {call.data}"
            await state.update_data(mentions=mentions)
            return await call.message.edit_text(  # type: ignore
                text=f"<b>Кого отметить?\nОтмечены {mentions.strip()}</b>",
                parse_mode="HTML",
                reply_markup=inline.get_users_keyboard(users, mentions.split()),
            )

        if call.data == "cancel_mentions":
            await state.update_data(mentions="")
            return await call.message.edit_text(  # type: ignore
                text="<b>Кого отметить?</b>",
                parse_mode="HTML",
                reply_markup=inline.get_users_keyboard(users),
            )

    return _get_mentions


def handle_event_update(on_success: Callable[..., Any], on_failure: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    async def _handle_event_update(
            call: CallbackQuery,
            *args: Any,
            state: FSMContext,
            scheduler: AsyncIOScheduler,
            session: AsyncSession,
            **kwargs: Any,
    ) -> Any:
        if call.data == "confirm":
            await push_arguments(on_success)(call, *args, state=state, session=session, scheduler=scheduler, **kwargs)
        elif call.data == "cancel":
            await push_arguments(on_failure)(call, *args, state=state, session=session, scheduler=scheduler, **kwargs)
        await state.clear()
        return await send_start_menu(call=call, state=state)

    return _handle_event_update


def process_events(process: Callable[..., Any]) -> Callable[..., Awaitable[Any]]:
    async def _process_events(call: CallbackQuery, *args: Any, state: FSMContext, **kwargs: Any) -> Any:
        if call.data and call.data.startswith("$"):
            return await push_arguments(process)(call, *args, state=state, **kwargs)
        if call.data == "back":
            await state.clear()
            await call.message.edit_text(  # type: ignore
                text="<b>Что хотите сделать?</b>",
                reply_markup=inline.event_interactions,
                parse_mode="HTML"
            )
    return _process_events
