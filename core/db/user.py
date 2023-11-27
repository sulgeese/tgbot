from psycopg2.extensions import connection
from core.utils.convert import py_to_sql


def add_user(conn: connection, user_id: int, username: str, first_name: str | None, last_name: str | None) -> None:
    data = ("({}, {}, {}, {})".format(*map(py_to_sql, [user_id, username, first_name, last_name])))
    with conn.cursor() as cursor:
        cursor.execute(f"""INSERT INTO groupusers VALUES {data};""")


def del_user(conn: connection, user_id: int) -> None:
    with conn.cursor() as cursor:
        cursor.execute(
            f"""DELETE FROM groupusers
                WHERE user_id={user_id};"""
        )