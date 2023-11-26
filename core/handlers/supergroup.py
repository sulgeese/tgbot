from aiogram import F, Router
from aiogram.types import Message

sgr_router = Router()
sgr_router.message.filter(F.chat.type == "supergroup")


@sgr_router.message()
async def supergroup_message_handler(message: Message):
    print(message)
