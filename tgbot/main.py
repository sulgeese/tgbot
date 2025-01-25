import asyncio
import logging
import os

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers.private_all import pr_all_router
from bot.handlers.private_members import pr_members_router
from bot.handlers.supergroup import sgr_router
from bot.middleware.db import DbSessionMiddleware
from bot.middleware.users import GroupMiddleware

from db.scheduler import start_scheduler
from db.engine import connect_to_db
from db.redis import redis

from settings import settings



async def start():
    os.environ["TZ"] = settings.other.timezone
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - '
               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
    bot = Bot(token=settings.bots.token)
    scheduler = await start_scheduler(bot)
    session_maker = await connect_to_db()

    dp = Dispatcher(scheduler=scheduler, storage=RedisStorage(redis=redis))

    dp.update.middleware(GroupMiddleware())
    dp.update.middleware(DbSessionMiddleware(session_maker))
    dp.include_router(sgr_router)
    dp.include_router(pr_members_router)
    dp.include_router(pr_all_router)

    async def start_bot():
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        finally:
            await bot.session.close()

    bot_task = asyncio.create_task(start_bot())

    await bot_task


if __name__ == '__main__':
    asyncio.run(start())
