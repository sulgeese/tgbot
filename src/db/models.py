from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import ForeignKey, BigInteger, DateTime, Integer, String, Text, Boolean

from datetime import datetime
from typing import Optional

from src.db.base import *


class GroupUsersModel(Base):
    __tablename__ = 'group_users'

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    in_group: Mapped[Boolean] = mapped_column(Boolean, default=True)
    events: Mapped[list["EventsModel"]] = relationship(back_populates='group_users')


class EventsModel(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(Text)
    date: Mapped[datetime] = mapped_column(DateTime)
    text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey(column='group_users.user_id'))
    mentions: Mapped[str] = mapped_column(Text)
    group_users: Mapped["GroupUsersModel"] = relationship(back_populates='events')
