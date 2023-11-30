from aiogram.types import TelegramObject
from aiogram import BaseMiddleware

from bot.settings import settings

from typing import Awaitable
from typing import Callable
from typing import Dict
from typing import Any


class GroupMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        if data['event_chat'].type == 'private' or \
           (data['event_chat'].type == 'supergroup' and data['event_chat'].id == settings.bots.supergroup_id):
            return await handler(event, data)
