from flask import (Flask,
                   render_template,
                   request,
                   url_for,
                   redirect,
                   flash,
                   get_flashed_messages)
import os

import requests
from urllib.parse import urlparse
import validators
from dotenv import load_dotenv
from datetime import date
from parser import parse_page

from datafunc import fetchall_query, fetchone_query, execute_query

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/add', methods=['POST'])
def add_url():
    current_url = request.form['url']
    if not validators.url(current_url):
        flash('Недействительный URL', 'error')
        return redirect(url_for('index'))

    url = urlparse(current_url)
    parsed_url = f"{url.scheme}://{url.netloc}"

    query_check = "SELECT id FROM urls WHERE name = %s"
    result = fetchone_query(query_check, (parsed_url,))

    if result:
        url_id = result['id']
        flash('URL уже существует', 'info')
    else:
        query_insert = ("INSERT INTO urls (name, created_at)"
                        "VALUES (%s, %s) RETURNING id")
        result = fetchone_query(query_insert,
                                (parsed_url, date.today()))
        url_id = result['id']
        flash('URL успешно добавлен', 'success')

    return redirect(url_for('url_info', id=url_id))


@app.route('/urls')
def urls():
    query_urls = """
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
    urls = fetchall_query(query_urls, ())
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['POST', 'GET'])
def url_info(id):
    query_url = "SELECT * FROM urls WHERE id = %s;"
    url = fetchone_query(query_url, (id,))

    query_checks = "SELECT * FROM url_checks WHERE url_id = %s;"
    url_checks = fetchall_query(query_checks, (id,))

    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'url_info.html',
        url=url,
        url_checks=url_checks,
        messages=messages,
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    query_url_name = "SELECT name FROM urls WHERE id = %s;"
    url_name = fetchone_query(query_url_name, (id,))

    if not url_name:
        flash('URL не найден', 'error')
        return redirect(url_for('url_info', id=id))

    try:
        response = requests.get(url_name['name'])
        status_code = response.status_code
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_info', id=id))

    url_data = parse_page(response.text)
    print(url_data)
    h1 = url_data['h1']
    title = url_data['title']
    description = url_data['description']
    query = ("INSERT INTO url_checks"
             "(url_id, status_code, h1, title, description, created_at)"
             "VALUES (%s, %s, %s, %s, %s, %s);")
    execute_query(query,
                  (id, status_code, h1, title, description, date.today()))
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('url_info', id=id))


@app.get('/404')
def missed_page():
    return render_template('404.html')


if __name__ == '__main__':
    app.run(debug=True)
