from typing import List

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data='confirm_creation'
            ),
            InlineKeyboardButton(
                text='Нет',
                callback_data='cancel_creation'
            )
        ]
    ]
)

events = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📆 Создать",
                callback_data="create_events"
            ),
            InlineKeyboardButton(
                text="✏️ Изменить",
                callback_data="edit_events"
            ),
        ],
        [
            InlineKeyboardButton(
                text="🗑️ Удалить",
                callback_data="delete_events"
            ),
            InlineKeyboardButton(
                text="🔍 Посмотреть",
                callback_data="search_events"
            ),
        ]
    ]
)


# Пиздец....
# Хуйпойми
def get_users_keyboard(users: List):
    users.append(("👥 Всех", " @".join(map(lambda user: user[1], users))))
    data, row = [], []
    for i, user in enumerate(users):
        row.append(InlineKeyboardButton(text=user[0], callback_data=f"@{user[1]}"))
        if i % 3 == 2:
            data.append(row)
            row = []
    if row: data.append(row)
    data.append([InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_mentions")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=data)
    return keyboard


def get_events_keyboard(_events: List):
    data, row = [], []
    for i, event in enumerate(_events, 0):
        row.append(InlineKeyboardButton(text=event.title, callback_data=f"${event.id}",))
        if i % 3 == 2:
            data.append(row)
            row = []
    if row: data.append(row)
    data.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=data)
    return keyboard


cancel_event = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="cancel_event"
            )
        ]
    ]
)

back = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="back"
            )
        ]
    ]
)

edit_events = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="📆 Дату",
                callback_data="edit_date"
            ),
            InlineKeyboardButton(
                text="📝 Название",
                callback_data="edit_title"
            ),
        ],
        [
            InlineKeyboardButton(
                text="📝 Текст",
                callback_data="edit_text"
            ),
            InlineKeyboardButton(
                text="👥 Упоминания",
                callback_data="edit_mentions"
            ),
        ],
[
            InlineKeyboardButton(
                text="✅ Подтвердить",
                callback_data="edit_confirm"
            ),
        ]
    ]
)
