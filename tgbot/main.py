import asyncio
import logging
import time
import os

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers.private_not_member import router as private_not_member_router
from bot.handlers.private_member import router as private_member_router
from bot.handlers.supergroup import router as supergroup_router
from bot.middleware.add_db import DbSessionMiddleware
from bot.middleware.check_chat_type import GroupMiddleware

from db.scheduler import start_scheduler
from db.engine import get_sessionmaker
from db.redis_instance import redis

from settings import settings


async def start():
    os.environ["TZ"] = settings.other.timezone
    time.tzset()
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - [%(levelname)s] - %(name)s - '
               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    bot = Bot(token=settings.bots.token)

    scheduler = await start_scheduler(bot)
    session_maker = await get_sessionmaker()

    dp = Dispatcher(scheduler=scheduler, storage=RedisStorage(redis=redis))
    dp.update.middleware(GroupMiddleware())
    dp.update.middleware(DbSessionMiddleware(session_maker))
    dp.include_router(supergroup_router)
    dp.include_router(private_member_router)
    dp.include_router(private_not_member_router)

    async def start_bot() -> None:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        finally:
            await redis.close()
            await bot.session.close()

    bot_task = asyncio.create_task(start_bot())

    await bot_task


if __name__ == '__main__':
    asyncio.run(start())
