from aiogram import Router, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER

from sqlalchemy.ext.asyncio import AsyncSession

from db.redis_instance import redis
from db.requests import update_user_status, update_user_status

router = Router()
router.message.filter(F.chat.type == "supergroup")
router.chat_member.filter(F.chat.type == "supergroup")
router.callback_query.filter(F.chat.type == "supergroup")


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def supergroup_user_join_handler(event: ChatMemberUpdated, session: AsyncSession):
    await update_user_status(
        session=session,
        user_id=event.new_chat_member.user.id,
        username=event.new_chat_member.user.username,
        first_name=event.new_chat_member.user.first_name,
        last_name=event.new_chat_member.user.last_name,
        in_group=True,
    )
    if await redis.exists("users"):
        await redis.delete("users")


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def supergroup_user_leave_handler(event: ChatMemberUpdated, session: AsyncSession):
    await update_user_status(
        session=session,
        user_id=event.old_chat_member.user.id,
        in_group=False,
    )
    if await redis.exists("users"):
        await redis.delete("users")
