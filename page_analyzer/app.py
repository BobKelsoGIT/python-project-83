from flask import (Flask,
                   render_template,
                   request,
                   url_for,
                   redirect,
                   flash,
                   abort)
import os
import requests
from dotenv import load_dotenv
from datetime import date
from page_analyzer.parser import parse_page
from url import validate_url, normalise_url
from .db import (get_url_by_name,
                 add_url,
                 get_urls_with_latest_checks,
                 get_url_by_id,
                 get_checks_by_url_id,
                 add_check)

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    search = request.args.get('search', '')
    return render_template('index.html', search=search)


@app.post('/urls')
def url_add():
    current_url = request.form['url']
    if not validate_url(current_url):
        flash('Некорректный URL', 'error')
        return render_template('index.html', search=current_url), 422
    normalised_url = normalise_url(current_url)
    result = get_url_by_name(normalised_url)

    if result:
        url_id = result['id']
        flash('Страница уже существует', 'info')
    else:
        url_id = add_url(normalised_url, date.today())
        flash('Страница успешно добавлена', 'success')

    return redirect(url_for('url_info', id=url_id))


@app.get('/urls')
def urls():
    urls = get_urls_with_latest_checks()
    return render_template('urls.html', urls=urls)


@app.route('/urls/<int:id>', methods=['POST', 'GET'])
def url_info(id):
    url = get_url_by_id(id)
    if not url:
        flash('Запрошенной страницы не существует', 'error')
        abort(404)

    url_checks = get_checks_by_url_id(id)
    return render_template(
        'url_info.html',
        url=url,
        url_checks=url_checks,
    )


@app.post('/urls/<int:id>/checks')
def url_check(id):
    url = get_url_by_id(id)
    if not url:
        flash('URL не найден', 'error')
        return redirect(url_for('url_info', id=id))
    try:
        response = requests.get(url['name'], timeout=10)
        response.raise_for_status()
        url_data = parse_page(response.text)
        add_check(
            id,
            response.status_code,
            url_data.get('h1'),
            url_data.get('title'),
            url_data.get('description')
        )
        flash('Страница успешно проверена', 'success')
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'error')

    return redirect(url_for('url_info', id=id))


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)
