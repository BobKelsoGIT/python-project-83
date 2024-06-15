import psycopg2
from psycopg2.extras import DictCursor
from datetime import date
from flask import current_app


def get_db_connection():
    database_url = current_app.config['DATABASE_URL']
    return psycopg2.connect(database_url)


def fetch_url_by_name(url_name):
    query = "SELECT id FROM urls WHERE name = %s"
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (url_name,))
            return cur.fetchone()


def insert_url(url, created_at):
    query = "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id"
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(query, (url, created_at))
            return cur.fetchone()


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
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query)
            return cur.fetchall()


def fetch_url_by_id(url_id):
    query = "SELECT * FROM urls WHERE id = %s"
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (url_id,))
            return cur.fetchone()


def fetch_checks_by_url_id(url_id):
    query = "SELECT * FROM url_checks WHERE url_id = %s"
    with get_db_connection() as conn:
        with conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute(query, (url_id,))
            return cur.fetchall()


def insert_check(url_id, status_code, h1, title, description):
    query = ("INSERT INTO url_checks"
             "(url_id, status_code, h1, title, description, created_at)"
             "VALUES "
             "(%s, %s, %s, %s, %s, %s)")
    with get_db_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                query,
                (url_id, status_code, h1, title, description, date.today())
            )
