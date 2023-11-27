from aiogram import F, Router
from aiogram.types import Message
from aiogram.filters.chat_member_updated import ChatMemberUpdatedFilter, JOIN_TRANSITION, LEAVE_TRANSITION

from core.db.user import add_user, del_user
from core.settings import settings

from psycopg2.extensions import connection

sgr_router = Router()
sgr_router.message.filter(F.chat.type == "supergroup", F.chat.type == settings.bots.supergroup_id)
sgr_router.my_chat_member.filter(F.chat.type == "supergroup", F.chat.type == settings.bots.supergroup_id)


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=JOIN_TRANSITION))
async def supergroup_message_handler(message: Message, conn: connection):
    add_user(
        conn=conn,
        user_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )


@sgr_router.chat_member(ChatMemberUpdatedFilter(member_status_changed=LEAVE_TRANSITION))
async def supergroup_message_handler(message: Message, conn: connection):
    del_user(
        conn=conn,
        user_id=message.from_user.id
    )