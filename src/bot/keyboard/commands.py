from aiogram.types import BotCommandScopeAllPrivateChats, BotCommand
from aiogram import Bot


async def set_commands(bot: Bot):
    commands = [
        BotCommand(
        )]
    await bot.delete_my_commands()
    await bot.set_my_commands(commands, BotCommandScopeAllPrivateChats())
