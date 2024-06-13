from flask import Flask, render_template, request, url_for, redirect, flash
import os
import psycopg2
import requests
from urllib.parse import urlparse
import validators
from dotenv import load_dotenv
from datetime import datetime

from psycopg2.extras import DictCursor

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template(
        'index.html',
    )


@app.route('/add', methods=['POST'])
def add_url():
    current_url = request.form['url']
    if validators.url(current_url):
        url = urlparse(current_url)
        parsed_url = f"{url.scheme}://{url.netloc}"
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO urls (name, created_at) VALUES (%s, %s)",
            (parsed_url, datetime.now().replace(microsecond=0))
        )
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))


@app.route('/urls')
def urls():
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=DictCursor)
    query_urls = (
        'SELECT '
        'urls.id AS id, '
        'urls.name AS name, '
        'url_checks.created_at AS last_check, '
        'url_checks.status_code AS status_code '
        'FROM urls '
        'LEFT JOIN url_checks '
        'ON urls.id = url_checks.url_id '
        'AND url_checks.id = ('
        'SELECT max(id) FROM url_checks '
        'WHERE urls.id = url_checks.url_id) '
        'ORDER BY urls.id DESC;'
    )
    cur.execute(query_urls)
    urls = cur.fetchall()
    conn.close()
    return render_template(
        'urls.html',
        urls=urls,
    )


@app.route('/urls/<int:id>', methods=['GET'])
def url_info(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=DictCursor)
    query_url = "SELECT * FROM urls WHERE id = %s;"
    cur.execute(query_url, (id,))
    url = cur.fetchone()

    query_checks = "SELECT * FROM url_checks WHERE url_id = %s;"
    cur.execute(query_checks, (id,))
    url_checks = cur.fetchall()
    conn.close()

    return render_template(
        'url_info.html',
        url=url,
        url_checks=url_checks,
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=DictCursor)
    url_id = id
    query_url_name = "SELECT name FROM urls WHERE id = %s;"
    cur.execute(query_url_name, (id,))
    url_name = cur.fetchone()
    status_code = requests.get(url_name[0]).status_code
    query = "INSERT INTO url_checks (url_id, status_code, created_at) VALUES (%s, %s, %s);"
    cur.execute(query, (url_id, status_code, datetime.now().replace(microsecond=0)))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for('url_info', id=id))


@app.get('/404')
def missed_page():
    return render_template(
        '404.html',
    )


if __name__ == '__main__':
    app.run(debug=True)
