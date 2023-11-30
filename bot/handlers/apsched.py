from core.settings import settings
from aiogram import Bot
from core.utils.entities import str_to_entities


async def send_message_by_date(bot: Bot, text: str, entities: str) -> None:
    await bot.send_message(chat_id=settings.bots.supergroup_id,
                           text=text,
                           entities=str_to_entities(entities),
                           reply_to_message_id=settings.bots.theme_id)
