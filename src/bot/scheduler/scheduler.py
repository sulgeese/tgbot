from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler_di import ContextSchedulerDecorator

from aiogram import Bot

from src.settings import settings


def run_and_get_scheduler(bot: Bot):
    jobstores = {'default': RedisJobStore(
        jobs_key='dispatched_trips_jobs',
        run_times_key='dispatched_trips_running',
        host=settings.redis.host,
        port=settings.redis.port,
    )
    }
    scheduler = ContextSchedulerDecorator(AsyncIOScheduler(timezone=settings.other.timezone, jobstores=jobstores))
    scheduler.ctx.add_instance(bot, declared_class=Bot)
    scheduler.start()
    return scheduler
