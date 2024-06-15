from flask import (Flask,
                   render_template,
                   request,
                   url_for,
                   redirect,
                   flash,
                   get_flashed_messages,
                   abort)
import os
import requests
from urllib.parse import urlparse
import validators
from dotenv import load_dotenv
from datetime import date
from page_analyzer.parser import parse_page
from db import (fetch_url_by_name,
                insert_url,
                fetch_urls_with_latest_checks,
                fetch_url_by_id,
                fetch_checks_by_url_id,
                insert_check)

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/add', methods=['POST'])
def add_url():
    current_url = request.form['url']
    if not validators.url(current_url):
        flash('Некорректный URL', 'error')
        return redirect(url_for('index'))

    url = urlparse(current_url)
    parsed_url = f"{url.scheme}://{url.netloc}"

    result = fetch_url_by_name(parsed_url)

    if result:
        url_id = result['id']
        flash('Страница уже существует', 'info')
    else:
        url_id = insert_url(parsed_url, date.today())['id']
        flash('Страница успешно добавлена', 'success')

    return redirect(url_for('url_info', id=url_id))


@app.route('/urls')
def urls():
    urls = fetch_urls_with_latest_checks()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['POST', 'GET'])
def url_info(id):
    url = fetch_url_by_id(id)
    if url is None:
        flash('Запрошенной страницы не существует', 'error')
        abort(404)

    url_checks = fetch_checks_by_url_id(id)
    messages = get_flashed_messages(with_categories=True)

    return render_template(
        'url_info.html',
        url=url,
        url_checks=url_checks,
        messages=messages,
    )


@app.post('/urls/<int:id>/checks')
def check_url(id):
    url = fetch_url_by_id(id)

    if not url:
        flash('URL не найден', 'error')
        return redirect(url_for('url_info', id=id))

    try:
        response = requests.get(url['name'], timeout=10)
        status_code = response.status_code
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_info', id=id))

    if status_code != 200:
        flash('Произошла ошибка при проверке', 'error')
        return redirect(url_for('url_info', id=id))

    url_data = parse_page(response.text)
    h1 = url_data['h1']
    title = url_data['title']
    description = url_data['description']

    insert_check(id, status_code, h1, title, description)
    flash('Страница успешно проверена', 'success')

    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    messages = get_flashed_messages(with_categories=True)
    return render_template('404.html', messages=messages), 404


if __name__ == '__main__':
    app.run(debug=True)
