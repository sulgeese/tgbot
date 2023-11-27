from psycopg2.extensions import connection
from core.db.other import db_tables


def create_table_group_users(conn: connection) -> None:
    if 'groupusers' not in db_tables(conn=conn):
        with conn.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE groupusers (
                   user_id int8 NOT NULL,
                   username varchar(32) NOT NULL,
                   first_name varchar(64),
                   last_name varchar(64)
                   );"""
            )
