from bot.utils.commands import set_commands
from bot.utils.convert import datetime_to_str
from bot.settings import settings

from datetime import datetime

from aiogram import Bot


async def on_startup(bot: Bot):
    await set_commands(bot)
    await bot.send_message(chat_id=settings.bots.admin_id,
                           text=f'Бот запущен <b>{datetime_to_str(datetime.now())}</b>',
                           parse_mode='HTML')


async def end_message(bot: Bot):
    await bot.send_message(chat_id=settings.bots.admin_id,
                           text=f'Бот остановлен <b>{datetime_to_str(datetime.now())}</b>',
                           parse_mode='HTML')
