from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='create_event',
            description='Создать напоминание'
        )]

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())
