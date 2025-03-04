from aiogram import Router, F
from aiogram.types import ChatMemberUpdated
from aiogram.filters import ChatMemberUpdatedFilter, IS_MEMBER, IS_NOT_MEMBER
from redis.asyncio import Redis

from sqlmodel.ext.asyncio.session import AsyncSession

from bot.handlers.utils import update_user


router = Router()

router.message.filter(F.chat.type == "supergroup")
router.chat_member.filter(F.chat.type == "supergroup")
router.callback_query.filter(F.chat.type == "supergroup")


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def supergroup_user_join_handler(event: ChatMemberUpdated, session: AsyncSession, redis: Redis) -> None:
    await update_user(event, session, redis, in_group=True)

@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> IS_NOT_MEMBER))
async def supergroup_user_leave_handler(event: ChatMemberUpdated, session: AsyncSession, redis: Redis) -> None:
    await update_user(event, session, redis, in_group=False)
