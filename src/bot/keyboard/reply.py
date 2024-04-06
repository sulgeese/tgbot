from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

web_app = WebAppInfo(url='https://sulgeese.github.io/')


start = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(
                text='📆 События'
            ),
            # KeyboardButton(
            #     text='💻 Перейти на сайт',
            #     web_app=web_app,
            # ),
        ]
    ],
    resize_keyboard=True,
)
