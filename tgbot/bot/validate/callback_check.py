import logging
from typing import Any, Callable, Awaitable
from functools import wraps

from aiogram.types import CallbackQuery, Message


logger = logging.getLogger(__name__)


def ensure_callback_message(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
    @wraps(func)
    async def wrapper(call: CallbackQuery, *args: Any, **kwargs: Any) -> Any:
        if isinstance(call.message, Message):
            return await func(call, *args, **kwargs)
        else:
            logger.warning(f"Callback message from_user {call.from_user.id} is None or Unreachable ")
            return None
    return wrapper
