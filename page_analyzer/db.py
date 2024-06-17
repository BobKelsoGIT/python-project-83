import psycopg2
from psycopg2.extras import DictCursor
from datetime import date
from flask import current_app


def get_db_connection():
    database_url = current_app.config['DATABASE_URL']
    return psycopg2.connect(database_url)


def execute_query(query, params=None, fetchone=False, fetchall=False):
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, params)
            if fetchone:
                return cur.fetchone()
            elif fetchall:
                return cur.fetchall()


def fetch_url_by_name(url_name):
    query = "SELECT id FROM urls WHERE name = %s"
    return execute_query(query, (url_name,), fetchone=True)


def insert_url(url, created_at):
    query = "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id"
    return execute_query(query, (url, created_at), fetchone=True)[0]


def fetch_urls_with_latest_checks():
    query = """
        SELECT
            urls.id AS id,
            urls.name AS name,
            url_checks.created_at AS last_check,
            url_checks.status_code AS status_code
        FROM urls
        LEFT JOIN url_checks
        ON urls.id = url_checks.url_id
        AND url_checks.id = (
            SELECT max(id) FROM url_checks
            WHERE urls.id = url_checks.url_id
        )
        ORDER BY urls.id DESC;
    """
    return execute_query(query, fetchall=True)


def fetch_url_by_id(url_id):
    query = "SELECT * FROM urls WHERE id = %s"
    return execute_query(query, (url_id,), fetchone=True)


def fetch_checks_by_url_id(url_id):
    query = "SELECT * FROM url_checks WHERE url_id = %s"
    return execute_query(query, (url_id,), fetchall=True)


def insert_check(url_id, status_code, h1, title, description):
    query = ("INSERT INTO url_checks"
             "(url_id, status_code, h1, title, description, created_at)"
             "VALUES "
             "(%s, %s, %s, %s, %s, %s)")
    execute_query(query,
                  (url_id, status_code, h1, title, description, date.today()))
