from uuid import uuid4, UUID
from datetime import datetime
from typing import Optional, List, Any

from pydantic import field_validator
from sqlalchemy import BIGINT
from sqlmodel import SQLModel, Field, Relationship

from bot.datetime_utils import parse_datetime


class UsersModel(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(default=None, unique=True, nullable=False, primary_key=True, sa_type=BIGINT)
    username: Optional[str] = Field(max_length=32, default=None)
    first_name: Optional[str] = Field(max_length=64, default=None)
    last_name: Optional[str] = Field(max_length=64)
    in_group: bool = Field(default=True)

    events: List["EventsModel"] = Relationship(back_populates="users")


class EventsModel(SQLModel, table=True):
    __tablename__ = "events"

    id: UUID = Field(primary_key=True, default_factory=uuid4, unique=True, nullable=False)
    title: str = Field(default="")
    date: datetime = Field(default=datetime.now())
    text: str = Field(default="")
    user_id: int = Field(default="", foreign_key="users.id", sa_type=BIGINT)
    mentions: str = Field(default="")

    users: Optional[UsersModel] = Relationship(back_populates='events')

    @field_validator("date", mode="before")
    @classmethod
    def parse_custom_date(cls, value: Any) -> Any:
        if isinstance(value, str):
            return parse_datetime(value)
        return value
