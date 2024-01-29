from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

web_app = WebAppInfo(url='http://127.0.0.1:8000')

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
