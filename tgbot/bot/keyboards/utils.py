from typing import List, Tuple

from db.models import UsersModel


def get_users_for_keyboard(users: List[UsersModel]) -> List[Tuple[str, str]]:
    result = []
    if users is None:
        return []
    for user in users:
        if user.last_name:
            result.append((f"{user.first_name} {user.last_name}", f"{user.username}"))
        else:
            result.append((f"{user.first_name}", f"{user.username}"))
    return result