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
def get_users_keyboard(user_list: List, dont_show: str = None) -> InlineKeyboardMarkup:
    user_list.append(("👥 Всех", " @".join(map(lambda _user: _user[1], user_list))))
    keyboard_rows, current_row = [], []
    if user_list:
        for i, user in enumerate(user_list):
            if dont_show and user[1] in dont_show:
                continue
            current_row.append(InlineKeyboardButton(text=user[0], callback_data=f"@{user[1]}"))
            if i % 3 == 2:
                keyboard_rows.append(current_row)
                current_row = []
        if current_row:
            keyboard_rows.append(current_row)
    keyboard_rows.append([
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_mentions"),
        InlineKeyboardButton(text="🔄 Сбросить", callback_data=f"cancel_mentions")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def get_events_keyboard(event_list: List) -> InlineKeyboardMarkup:
    keyboard_rows, current_row = [], []
    if event_list:
        for i, event in enumerate(event_list):
            current_row.append(InlineKeyboardButton(
                text=event.get("title"),
                callback_data=f"${event.get("event_id")}"
            ))
            if i % 3 == 2:
                keyboard_rows.append(current_row)
                current_row = []
        if current_row:
            keyboard_rows.append(current_row)
    keyboard_rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


event_search_back = InlineKeyboardMarkup(
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
                text="✅ Подтвердить",
                callback_data="edit_confirm"
            ),
        ]
    ]
)