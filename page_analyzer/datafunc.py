import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


def get_db_connection():
    return psycopg2.connect(DATABASE_URL)


def fetch_query(query, params, param):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            if param == 'one':
                return cur.fetchone()
            else:
                return cur.fetchall()


def execute_query(query, params):
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
