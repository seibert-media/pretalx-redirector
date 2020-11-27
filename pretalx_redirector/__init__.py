import logging
import psycopg2
from configparser import ConfigParser
from flask import Flask, redirect
from os import environ
from uuid import uuid4

PROJECT_ROOT = dirname(dirname(abspath(__file__)))
FLASK_ROOT = dirname(abspath(__file__))

app = Flask(__name__)
app.secret_key = str(uuid4())

if not app.debug:
    log = logging.StreamHandler()
    log.setLevel(logging.INFO)
    app.logger.addHandler(log)

config = ConfigParser()
config.read(environ['APP_CONFIG'])

pg_pool = psycopg2.pool.ThreadedConnectionPool(
    minconn=1,
    maxconn=config['database']['max_conns'],
    user=config['database']['user'],
    password=config['database']['pass'],
    database=config['database']['database'],
    host=config['database']['host']
)

def get_submission_details_for_code(code):
    conn = pg_pool.getconn()

    cursor = conn.cursor()
    cursor.execute('SELECT s.code, e.slug FROM submission_submission s LEFT JOIN event_event e ON s.event_id = e.id WHERE s.code = %s LIMIT 1', (code,))
    result = cursor.fetchone()

    pg_pool.putconn(conn)

    return result


@app.route('/')
def index():
    return redirect('https://talks.seibert-media.net')


@app.route('/<code>')
def redirect_to_talk_url(code):
    details = get_submission_details_for_code(code)

    if details:
        return redirect('https://talks.seibert-media.net/{slug}/talk/{code}/feedback/'.format(
            slug=details[1],
            code=details[0],
        ))

    return redirect('https://talks.seibert-media.net')
