from bot.filters.user import UserNotInGroup

from aiogram.types import Message
from aiogram import Router, F

pr_all_router = Router()

pr_all_router.message.filter(F.chat.type == "private", UserNotInGroup())
pr_all_router.chat_member.filter(F.chat.type == "private", UserNotInGroup())
pr_all_router.callback_query.filter(F.message.chat.type == "private", UserNotInGroup())


@pr_all_router.message()
async def botic(message: Message):
    await message.answer(text='ты не в группе')
