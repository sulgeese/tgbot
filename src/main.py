import asyncio
import logging

from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.redis import RedisStorage
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from hypercorn.asyncio import serve
from hypercorn.config import Config

from app.middleware import create_db_middleware
from app.router import router
from bot.handlers.basic import end_message, on_startup
from bot.handlers.privateall import pr_all_router
from bot.handlers.privatemembers import pr_members_router
from bot.handlers.supergroup import sgr_router
from bot.middleware.db import DbSessionMiddleware
from bot.middleware.users import GroupMiddleware
from bot.scheduler.scheduler import run_and_get_scheduler
from db.engine import connect_to_db
from db.redis import redis
from settings import settings


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

    app = FastAPI(title='Дед Инсайд')
    origins = [
        "http://127.0.0.1:8000",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    db_middleware = create_db_middleware(session_maker=session_maker)
    app.middleware("http")(db_middleware)
    app.include_router(router)
    config = Config()
    logging.getLogger("hypercorn").setLevel(logging.DEBUG)

    dp = Dispatcher(scheduler=scheduler, storage=RedisStorage(redis=redis))
    dp.startup.register(on_startup)
    dp.shutdown.register(end_message)
    dp.update.middleware(GroupMiddleware())
    dp.update.middleware(DbSessionMiddleware(session_maker))
    dp.include_router(pr_members_router)
    dp.include_router(pr_all_router)
    dp.include_router(sgr_router)

    async def start_bot():
        try:
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)
        finally:
            await bot.session.close()

    async def start_app():
        await serve(app, config)

    bot_task = asyncio.create_task(start_bot())
    app_task = asyncio.create_task(start_app())

    await bot_task
    await app_task


if __name__ == '__main__':
    asyncio.run(start())
