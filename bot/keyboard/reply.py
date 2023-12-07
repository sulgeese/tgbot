from aiogram.types import ReplyKeyboardMarkup
from aiogram.types import KeyboardButton
from aiogram.types import WebAppInfo

web_app = WebAppInfo(url='https://sulgeese.github.io/')

cancel_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Отмена')
        ]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)


webapp_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='Перейти на сайт',
                web_app=web_app,
            )

        ]
    ],
    resize_keyboard=True,
)
