from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text="📆 События"
            ),
        ]
    ],
    resize_keyboard=True,
)
