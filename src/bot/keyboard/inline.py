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
def get_users_keyboard(users: List, dont_show: str = None) -> InlineKeyboardMarkup:
    users.append(("👥 Всех", " @".join(map(lambda _user: _user[1], users))))
    data, row = [], []
    for i, user in enumerate(users):
        if dont_show:
            if user[1] in dont_show:
                continue
        row.append(InlineKeyboardButton(text=user[0], callback_data=f"@{user[1]}"))
        if i % 3 == 2:
            data.append(row)
            row = []
    if row: data.append(row)
    data.append([InlineKeyboardButton(text="✅ Сохранить", callback_data=f"confirm_mentions"),
                 InlineKeyboardButton(text="🔄 Сбросить", callback_data=f"cancel_mentions")])
    keyboard = InlineKeyboardMarkup(inline_keyboard=data)
    return keyboard


def get_events_keyboard(_events: List):
    data, row = [], []
    for i, event in enumerate(_events, 0):
        event_id, title = event.get("event_id"), event.get("title")
        row.append(InlineKeyboardButton(text=title, callback_data=f"${event_id}", ))
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
                text="✅ Сохранить",
                callback_data="edit_confirm"
            ),
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="edit_cancel"
            ),
        ]
    ]
)
