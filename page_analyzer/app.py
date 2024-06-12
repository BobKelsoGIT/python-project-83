from flask import Flask, render_template, request, url_for, redirect, flash
import os
import psycopg2
from urllib.parse import urlparse
import validators
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def index():
    return render_template(
        'index.html',
    )


@app.route('/check', methods=['POST'])
def check_url():
    current_url = request.form['url']
    if validators.url(current_url):
        url = urlparse(current_url)
        parsed_url = f"{url.scheme}://{url.netloc}"
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT INTO urls (name) VALUES (%s)", (parsed_url,))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(url_for('index'))


@app.route('/urls')
def urls():
    return render_template(
        'urls.html',
    )


if __name__ == '__main__':
    app.run(debug=True)
