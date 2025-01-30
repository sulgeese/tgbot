from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo


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
