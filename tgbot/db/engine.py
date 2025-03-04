import logging

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import URL
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel

from settings import settings

logger = logging.getLogger(__name__)


async def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    url = URL.create(
        drivername="postgresql+asyncpg",
        username=settings.db.username,
        password=settings.db.password,
        host=settings.db.host,
        port=settings.db.port,
        database=settings.db.database,
    )
    async_engine = create_async_engine(url=url)

    try:
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Created database tables successfully")
        return async_sessionmaker(
            bind=async_engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        raise