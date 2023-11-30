from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped

from bot.db.base import *

from sqlalchemy import ForeignKey
from sqlalchemy import BigInteger
from sqlalchemy import DateTime
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text

from datetime import datetime
from typing import Optional


class GroupUsersModel(Base):
    __tablename__ = 'group_users'

    user_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, primary_key=True)
    username: Mapped[Optional[str]] = mapped_column(String(32))
    first_name: Mapped[Optional[str]] = mapped_column(String(64))
    last_name: Mapped[Optional[str]] = mapped_column(String(64))
    events: Mapped[list["EventsModel"]] = relationship(back_populates='group_users')


class EventsModel(Base):
    __tablename__ = 'events'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    date: Mapped[datetime] = mapped_column(DateTime)
    text: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(ForeignKey(column='group_users.user_id'))
    group_users: Mapped["GroupUsersModel"] = relationship(back_populates='events')
