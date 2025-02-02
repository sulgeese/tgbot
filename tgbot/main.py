import asyncio
import logging
import time
import os

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers import private_member_router, supergroup_router, private_not_member_router
from bot.middleware import DbSessionMiddleware
from bot.middleware import GroupMiddleware

from db.scheduler import start_scheduler
from db.engine import get_sessionmaker
from db.redis_instance import redis

from settings import settings


async def start():
    os.environ["TZ"] = settings.other.timezone
    time.tzset()
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - [%(levelname)s] - %(name)s - '
               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    bot = Bot(token=settings.bots.token)
    session_maker = await get_sessionmaker()
    scheduler = await start_scheduler(bot)
    dispatcher = Dispatcher(
        events_isolation=SimpleEventIsolation(),
        scheduler=scheduler,
        storage=RedisStorage(redis=redis),
    )
    dispatcher.update.middleware(GroupMiddleware())
    dispatcher.update.middleware(DbSessionMiddleware(session_maker))
    # dispatcher.include_router(supergroup_router)
    dispatcher.include_router(private_member_router)
    # dispatcher.include_router(private_not_member_router)

    async def start_bot() -> None:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dispatcher.start_polling(bot)
        finally:
            await redis.close()
            await bot.session.close()

    bot_task = asyncio.create_task(start_bot())

    await bot_task


if __name__ == "__main__":
    asyncio.run(start())