import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import mapped_column, relationship, Mapped
from sqlalchemy import ForeignKey, BigInteger, DateTime, String, Text, Boolean, Uuid

from db.base import *


class UsersModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger(), unique=True, nullable=False, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    in_group: Mapped[bool] = mapped_column(Boolean(), default=True)
    events: Mapped[list["EventsModel"]] = relationship(back_populates="users")


class EventsModel(Base):
    __tablename__ = "events"

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4(), unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(Text)
    date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    text: Mapped[Optional[str]] = mapped_column(Text)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey(column="users.id"))
    mentions: Mapped[Optional[str]] = mapped_column(Text)
    users: Mapped["UsersModel"] = relationship(back_populates='events')
