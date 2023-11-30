from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.engine import URL


def create_engine(drivername: str, username: str, password: str, host: str, port: int, database: str) -> AsyncEngine:
    url = URL.create(
        drivername=drivername,
        username=username,
        password=password,
        host=host,
        port=port,
        database=database,
    )
    return create_async_engine(url=url)


async def proceed_schemas(engine: AsyncEngine, metadata) -> None:
    async with engine.begin() as connect:
        await connect.run_sync(metadata.create_all)


def get_session_maker(engine: AsyncEngine) -> async_sessionmaker:
    return async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

