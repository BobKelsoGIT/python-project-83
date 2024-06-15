import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()


def get_db_connection(app):
    database_url = app.config['DATABASE_URL']
    return psycopg2.connect(database_url)


def fetch_query(app, query, params, param):
    with get_db_connection(app) as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            if param == 'one':
                return cur.fetchone()
            else:
                return cur.fetchall()


def execute_query(app, query, params):
    with get_db_connection(app) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            conn.commit()
