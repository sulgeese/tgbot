from aiogram import Bot

from src.bot.utils.entities import str_to_entities
from src.settings import settings


async def send_message_by_date(bot: Bot, title: str, text: str, entities: str) -> None:
    ent = [{'type': 'bold', 'offset': 0, 'length': len(title)}] + str_to_entities(entities, len(title) + 1)
    await bot.send_message(chat_id=settings.bots.supergroup_id,
                           text=f"{title}\n{text}",
                           entities=ent,
                           reply_to_message_id=settings.bots.theme_id,
                           )
