from fastapi import Request, Response
from sqlalchemy.ext.asyncio import async_sessionmaker


def create_db_middleware(session_maker: async_sessionmaker):
    async def db_middleware(request: Request, call_next):
        response = Response("Internal server error", status_code=500)
        try:
            async with session_maker() as session:
                request.state.session = session
                response = await call_next(request)
                return response
        except Exception:
            return response

    return db_middleware
