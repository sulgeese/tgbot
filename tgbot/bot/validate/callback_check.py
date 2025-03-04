import logging
from typing import Any

from aiogram.types import CallbackQuery, Message


logger = logging.getLogger(__name__)


def callback_message_check(call: CallbackQuery) -> Any:
    if isinstance(call.message, Message):
        return call.message
    logger.error("Could not get message from callback")