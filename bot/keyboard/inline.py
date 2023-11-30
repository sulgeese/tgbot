from aiogram.types import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton


confirmation = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data='confirm'
            ),
            InlineKeyboardButton(
                text='Нет',
                callback_data='cancel'
            )
        ]
    ]
)
