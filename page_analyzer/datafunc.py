import psycopg2
from psycopg2.extras import DictCursor
import os

DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def fetchone_query(query, params):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchone()


def fetchall_query(query, params):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            return cur.fetchall()


def execute_query(query, params):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
