from bot.handlers.privatemembers import pr_members_router
from bot.handlers.privateall import pr_all_router
from bot.handlers.supergroup import sgr_router
from bot.scheduler.scheduler import run_and_get_scheduler
from bot.handlers.basic import end_message
from bot.handlers.basic import on_startup
from bot.middleware.users import GroupMiddleware
from bot.middleware.db import DbSessionMiddleware
from bot.db.engine import connect_to_db
from bot.settings import settings
from bot.db.redis import redis

from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Dispatcher
from aiogram import Bot

import asyncio
import logging


async def start():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - '
               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

    bot = Bot(token=settings.bots.token)
    scheduler = run_and_get_scheduler(bot)
    session_maker = await connect_to_db()

    dp = Dispatcher(scheduler=scheduler, storage=RedisStorage(redis=redis))
    dp.startup.register(on_startup)
    dp.shutdown.register(end_message)
    dp.update.middleware(GroupMiddleware())
    dp.update.middleware(DbSessionMiddleware(session_maker))
    dp.include_router(pr_members_router)
    dp.include_router(pr_all_router)
    dp.include_router(sgr_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
