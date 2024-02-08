from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm = InlineKeyboardMarkup(
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

events = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='📆 Создать',
                callback_data='create_events'
            ),
            InlineKeyboardButton(
                text='✏️ Изменить',
                callback_data='edit_events'
            ),
        ],
        [
            InlineKeyboardButton(
                text='🗑️ Удалить',
                callback_data='delete_events'
            ),
            InlineKeyboardButton(
                text='🔍 Посмотреть',
                callback_data='search_events'
            ),
        ]
    ]
)


# Пиздец....
# Хуйпойми
def get_users(users: List):
    users.append(("👥 Всех", "@all"))
    data, row = [], []
    for i in range(len(users)):
        row.append(
            InlineKeyboardButton(
                text=users[i][0],
                callback_data=f"@{users[i][1]}",
            )
        )
        if i % 3 == 2:
            data.append(row)
            row = []
    if row: data.append(row)
    data.append([InlineKeyboardButton(
        text="✅ Подтвердить",
        callback_data=f"confirm_mentions",
    )])
    keyboard = InlineKeyboardMarkup(inline_keyboard=data)
    return keyboard
