from psycopg2.extensions import connection


def db_tables(conn: connection) -> list:
    with conn.cursor() as cursor:
        sql = "SELECT table_name FROM information_schema.tables WHERE table_schema='public'"
        cursor.execute(sql)
        return cursor.fetchall()[0]
