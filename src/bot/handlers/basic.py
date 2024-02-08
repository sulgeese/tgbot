from datetime import datetime

from aiogram import Bot

from src.bot.keyboard.commands import set_commands
from src.utils import datetime_to_str
from src.settings import settings


async def on_startup(bot: Bot):
    # await set_commands(bot)
    await bot.send_message(chat_id=settings.bots.admin_id,
                           text=f'Бот запущен <b>{datetime_to_str(datetime.now())}</b>',
                           parse_mode='HTML')


async def end_message(bot: Bot):
    await bot.send_message(chat_id=settings.bots.admin_id,
                           text=f'Бот остановлен <b>{datetime_to_str(datetime.now())}</b>',
                           parse_mode='HTML')
