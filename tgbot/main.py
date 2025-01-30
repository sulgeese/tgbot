import asyncio
import logging
import time
import os

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import SimpleEventIsolation
from aiogram.fsm.storage.redis import RedisStorage

from bot.handlers.event_actions.private_member2 import router as private_member2_router
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
        level=logging.DEBUG,
        format='%(asctime)s - [%(levelname)s] - %(name)s - '
               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S',
    )
    logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)
    logging.getLogger('apscheduler').setLevel(logging.DEBUG)
    session_maker = await get_sessionmaker()
    def create_dispatcher():
        dispatcher = Dispatcher(
            events_isolation=SimpleEventIsolation(),
            scheduler=scheduler,
            storage=RedisStorage(redis=redis),
        )
        dispatcher.update.middleware(GroupMiddleware())
        dispatcher.update.middleware(DbSessionMiddleware(session_maker))
        # dispatcher.include_router(supergroup_router)
        dispatcher.include_router(private_member2_router)
        # dispatcher.include_router(private_not_member_router)


        return dispatcher

    bot = Bot(token=settings.bots.token)

    scheduler = await start_scheduler(bot)




    dp = create_dispatcher()
    async def start_bot() -> None:
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        finally:
            await redis.close()
            await bot.session.close()

    bot_task = asyncio.create_task(start_bot())

    await bot_task


if __name__ == "__main__":
    asyncio.run(start())