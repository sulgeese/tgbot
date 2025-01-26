from aiogram import Router, F
from aiogram.types import Message

from bot.filters.user import UserNotInGroup


router = Router()

router.message.filter(F.chat.type == "private", UserNotInGroup())
router.chat_member.filter(F.chat.type == "private", UserNotInGroup())
router.callback_query.filter(F.message.chat.type == "private", UserNotInGroup())


@router.message()
async def botic(message: Message):
    await message.answer(text='ты не в группе')
