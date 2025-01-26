import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import URL

from settings import settings
from db.base import *

logger = logging.getLogger(__name__)


async def get_sessionmaker() -> async_sessionmaker:
    url = URL.create(
        drivername=settings.db.drivername,
        username=settings.db.username,
        password=settings.db.password,
        host=settings.db.host,
        port=settings.db.port,
        database=settings.db.database,
    )
    async_engine = create_async_engine(url=url)

    try:
        async with async_engine.begin() as connect:
            await connect.run_sync(Base.metadata.create_all)
        logger.info("Created database tables successfully")
        return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise