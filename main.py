from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from core.db.create import create_table_group_users
from core.db.connect import create_connection
from core.settings import settings
from core.handlers.private import pr_router
from core.handlers.supergroup import sgr_router
from core.handlers.basic import on_startup, end_message

import asyncio
import logging


async def start():
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - [%(levelname)s] - %(name)s - '
               '(%(filename)s).%(funcName)s(%(lineno)d) - %(message)s',
        datefmt='%d.%m.%Y %H:%M:%S',
    )

    bot = Bot(token=settings.bots.bot_token)

    jobstores = {'default': RedisJobStore(
        jobs_key='dispatched_trips_jobs',
        run_times_key='dispatched_trips_running',
        host='localhost',
        db=2,
        port=6379,
    )}

    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone=settings.bots.time_zone, jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.start()

    storage = RedisStorage.from_url('redis://localhost:6379/0')

    connection = create_connection(
        db_name=settings.db.db_name,
        db_user=settings.db.db_user,
        db_password=settings.db.db_password,
        db_host=settings.db.db_host,
        db_port=settings.db.db_port,
    )
    connection.autocommit = True
    create_table_group_users(connection)

    dp = Dispatcher(scheduler=scheduler, storage=storage, conn=connection)
    dp.startup.register(on_startup)
    dp.shutdown.register(end_message)
    dp.include_router(pr_router)
    dp.include_router(sgr_router)

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == '__main__':
    asyncio.run(start())
