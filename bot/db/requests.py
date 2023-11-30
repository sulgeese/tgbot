from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession


def insert_user(session: AsyncSession, user_id: int, username: str, first_name: str | None, last_name: str | None) -> None:
    pass


def del_user(session: AsyncSession, user_id: int) -> None:
    pass


def insert_event(session: AsyncSession, date: datetime, text: str, user_id: int) -> None:
    pass
