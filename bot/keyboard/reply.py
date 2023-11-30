from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton


cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отмена')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True)
