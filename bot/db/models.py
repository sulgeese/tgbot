from datetime import datetime
from typing import Optional

from sqlalchemy import ForeignKey, String, BigInteger, DateTime, Integer
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase


class Base(AsyncAttrs, DeclarativeBase):
    pass


class GroupUsersModel(Base):
    __tablename__ = 'group_users'

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))


class EventsModel(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    text: Mapped[str] = mapped_column(String())
    user_id: Mapped[int] = mapped_column(ForeignKey(column='group_users.user_id'))
