from aiogram.types import BotCommandScopeAllPrivateChats
from aiogram.types import BotCommand
from aiogram import Bot


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
            command='create_event',
            description='Создать напоминание'
        )]

    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())
