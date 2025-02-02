from typing import List, Tuple

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from db.models import EventsModel, UsersModel
from .utils import get_users_for_keyboard


confirm = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text='Да',
                callback_data="confirm"
            ),
            InlineKeyboardButton(
                text='Нет',
                callback_data="cancel"
            )
        ]
    ]
)

event_interactions = InlineKeyboardMarkup(
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
                callback_data="confirm"
            ),
            InlineKeyboardButton(
                text="❌ Отмена",
                callback_data="cancel"
            ),
        ]
    ]
)

event_back = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="event_search_back",
            )
        ]
    ]
)


def get_users_keyboard(users: List[UsersModel], ignore_username_list: List[str] = ()) -> InlineKeyboardMarkup:
    user_list = get_users_for_keyboard(users)
    if len(user_list) != len(ignore_username_list):
        user_list.append(("👥 Всех", "all"))
    keyboard_rows, current_row = [], []
    keyboard_width = 3
    for name, username in map(lambda x: (x[0], f"@{x[1]}"), user_list):
        if ignore_username_list and username in ignore_username_list:
            continue
        current_row.append(InlineKeyboardButton(text=name, callback_data=username))
        if len(current_row) == keyboard_width:
            keyboard_rows.append(current_row)
            current_row = []
    if current_row:
        keyboard_rows.append(current_row)
    keyboard_rows.append([
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_mentions"),
        InlineKeyboardButton(text="🔄 Сбросить", callback_data=f"cancel_mentions")]
    )
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def get_events_keyboard(events: List[EventsModel]) -> InlineKeyboardMarkup:
    keyboard_rows, current_row = [], []
    keyboard_width = 3
    if events:
        for event in events:
            current_row.append(InlineKeyboardButton(
                text=event.title,
                callback_data=f"${event.id}"
            ))
            if len(current_row) == keyboard_width:
                keyboard_rows.append(current_row)
                current_row = []
        if current_row:
            keyboard_rows.append(current_row)
    keyboard_rows.append([InlineKeyboardButton(text="⬅️ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
