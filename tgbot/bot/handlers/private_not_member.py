from aiogram import Router, F
from aiogram.types import Message

from bot.filters.user import UserInGroup


router = Router()

router.message.filter(F.chat.type == "private", ~UserInGroup())
router.chat_member.filter(F.chat.type == "private", ~UserInGroup())
router.callback_query.filter(F.message.chat.type == "private", ~UserInGroup())


@router.message()
async def not_in_group_message(message: Message) -> None:
    await message.answer(text='ты не в группе')
