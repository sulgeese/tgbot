from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy import URL

from src.settings import settings
from src.db.base import *


async def connect_to_db() -> async_sessionmaker:
    url = URL.create(
        drivername=settings.db.drivername,
        username=settings.db.username,
        password=settings.db.password,
        host=settings.db.host,
        port=settings.db.port,
        database=settings.db.database,
    )
    async_engine = create_async_engine(url=url)
    async with async_engine.begin() as connect:
        await connect.run_sync(Base.metadata.create_all)
    return async_sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

