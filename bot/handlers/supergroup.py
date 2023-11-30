from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION

from core.db.requests import insert_user, del_user

from sqlalchemy.ext.asyncio import AsyncSession

sgr_router = Router()


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def supergroup_message_handler(message: Message, session: AsyncSession):
    insert_user(
        session=session,
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def supergroup_message_handler(message: Message, session: AsyncSession):
    del_user(
        session=session,
        user_id=message.from_user.id,
    )
