from aiogram.filters import BaseFilter
from aiogram.types import Message

from datetime import datetime


class DateNotPassed(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        try:
            msg_date = datetime.strptime(message.text, "%d.%m.%Y %H:%M")
            return datetime.now() < msg_date
        except ValueError:
            return False


class DateFilter(BaseFilter):
    def __init__(self):
        pass

    async def __call__(self, message: Message) -> bool:
        try:
            datetime.strptime(message.text, "%d.%m.%Y %H:%M")
            return True
        except ValueError:
            return False
