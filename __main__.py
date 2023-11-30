from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from bot.handlers.privatemembers import pr_members_router
from bot.handlers.privateall import pr_all_router
from bot.handlers.supergroup import sgr_router
from bot.handlers.basic import end_message
from bot.handlers.basic import on_startup
from bot.middleware.users import GroupMiddleware
from bot.middleware.db import DbSessionMiddleware
from bot.db.engine import get_session_maker
from bot.db.engine import proceed_schemas
from bot.db.engine import create_engine
from bot.db.base import Base
from bot.settings import settings
from bot.misc import redis

from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher

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

    jobstores = {'default': RedisJobStore(
        jobs_key='dispatched_trips_jobs',
        run_times_key='dispatched_trips_running',
        host='localhost',
        db=2,
        port=6379,
    )}

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone=settings.other.timezone, jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.start()

    async_engine = create_engine(
        drivername=settings.db.drivername,
        username=settings.db.username,
        password=settings.db.password,
        host=settings.db.host,
        port=settings.db.port,
        database=settings.db.database,
    )
    session_maker = get_session_maker(async_engine)
    await proceed_schemas(async_engine, Base.metadata)

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
