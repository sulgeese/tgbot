from aiogram import Bot

from datetime import datetime

from core.settings import settings
from core.utils.commands import set_commands
from core.utils.date import datetime_to_str


async def start_message(bot: Bot):
    await set_commands(bot)
    await bot.send_message(chat_id=settings.bots.admin_id,
                           text=f'Бот запущен <b>{datetime_to_str(datetime.now())}</b>',
                           parse_mode='HTML')


async def end_message(bot: Bot):
    await bot.send_message(chat_id=settings.bots.admin_id,
                           text=f'Бот остановлен <b>{datetime_to_str(datetime.now())}</b>',
                           parse_mode='HTML')