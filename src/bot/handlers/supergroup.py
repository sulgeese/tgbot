from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION
from aiogram.types import Message
from aiogram import Router, F

from sqlalchemy.ext.asyncio import AsyncSession

from src.db.requests import insert_user, del_user
from src.db.redis import redis


sgr_router = Router()
sgr_router.message.filter(F.chat.type == "supergroup")
sgr_router.chat_member.filter(F.chat.type == "supergroup")
sgr_router.callback_query.filter(F.chat.type == "supergroup")


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def supergroup_message_handler(message: Message, session: AsyncSession):
    await insert_user(
        session=session,
        user_id=message.new_chat_member.user.id,
        username=message.new_chat_member.user.username,
        first_name=message.new_chat_member.user.first_name,
        last_name=message.new_chat_member.user.last_name,
    )
    await redis.delete('users')


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def supergroup_message_handler(message: Message, session: AsyncSession):
    await del_user(
        session=session,
        user_id=message.old_chat_member.user.id,
    )
    await redis.delete('users')
