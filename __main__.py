from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from bot.settings import settings
from bot.handlers.private import pr_router
from bot.handlers.supergroup import sgr_router
from bot.handlers.basic import on_startup, end_message
from bot.db.models import Base
from bot.db.engine import create_engine, proceed_schemas, get_session_maker
from bot.middleware.group import GroupMiddleware
from bot.middleware.db import DbSessionMiddleware

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

    storage = RedisStorage.from_url('redis://localhost:6379/0')

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

    dp = Dispatcher(scheduler=scheduler, storage=storage)
    dp.startup.register(on_startup)
    dp.shutdown.register(end_message)
    dp.include_router(pr_router)
    dp.include_router(sgr_router)
    dp.update.middleware(GroupMiddleware())
    dp.update.middleware(DbSessionMiddleware(session_maker))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
