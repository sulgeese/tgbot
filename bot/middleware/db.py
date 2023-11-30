from typing import Callable, Awaitable, Dict, Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_maker):
        super().__init__()
        self.session_maker = session_maker

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any],
    ) -> Any:
        async with self.session_maker() as session:
            data["session"] = session
            return await handler(event, data)
