from flask import Flask, make_response, render_template, request, redirect, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit, sqlite3, time, datetime, sys

# app info

app = Flask(__name__)
app.config.from_object(__name__)

app.config.update(dict(
    DB_NAME = 'database.db',
    DEFAULT_DURATION = 30,  # minutes
    DB_CLEAR_INTERVAL_HRS = 6,  # hours
    COOKIE_TIME = 1     # days
))
# NOTE: Chrome cookies expire too early

'''
database functions
'''

def sched_clean_db():
    # schedule DB cleans every 6 hours
    db_clear_sched = BackgroundScheduler()
    db_clear_sched.start()
    db_clear_sched.add_job(
        func = clear_db_old,
        trigger = IntervalTrigger(hours = app.config['DB_CLEAR_INTERVAL_HRS']),
        replace_existing = True
    )

    # set DB clear process to shutdown with app
    atexit.register(lambda: db_clear_sched.shutdown())

def init_db():
    con = sqlite3.connect(app.config['DB_NAME'])
    with app.open_resource('schema.sql', mode='r') as f:
        con.cursor().executescript(f.read())
    con.commit()
    con.close()

def clear_db_old():
    con = sqlite3.connect(app.config['DB_NAME'])
    cur = con.cursor()
    cur.execute('delete from links where ? > expires', (datetime.datetime.now(),))
    cur.execute('delete from cookies where ? > expires', (datetime.datetime.now(),))
    con.commit()
    con.close()

def get_current_url(alias):
    con = sqlite3.connect(app.config['DB_NAME'])
    cur = con.cursor()
    cur.execute('select url from links where alias = ? and ? < expires',
    (alias, datetime.datetime.now(),))
    url = cur.fetchone()
    con.close()
    return url

def add_cookie():
    con = sqlite3.connect(app.config['DB_NAME'])
    cur = con.cursor()

    cookie_expires = datetime.datetime.now() + datetime.timedelta(days
    = app.config['COOKIE_TIME'])
    cur.execute('insert into cookies (expires) values (?)', (cookie_expires,))
    cookie_id = str(cur.lastrowid)
    con.commit()
    con.close()

    return (cookie_id, cookie_expires)

def add_link(alias, original_url, duration, cookie_id):
    con = sqlite3.connect(app.config['DB_NAME'])
    cur = con.cursor()
    cur.execute('insert into links (alias, url, expires, cookie_id) values' \
    '(?, ?, ?, ?)', (alias, original_url, datetime.datetime.now() +
    datetime.timedelta(minutes = duration), cookie_id,))
    con.commit()
    con.close()

'''
view functions
'''

@app.route('/')
def index():
    con = sqlite3.connect(app.config['DB_NAME'])
    cur = con.cursor()
    cur.execute('select * from links where cookie_id = ?', (request.cookies.get('id'),))
    links = cur.fetchall()
    con.close()

    return render_template('index.html', links = links)

# utilize short link
@app.route('/link/<alias>')
def link(alias):
    url = get_current_url(alias)
    if url is None:
        return render_template(
            'error.html',
        msg = 'There is no tiny link with that alias. ' \
        'Please check the URL or create a link on the homepage.'
    ), 404

    return redirect(url[0])

# create short link
@app.route('/create')
def create_tiny():
    original_url = request.args.get('url')
    alias = request.args.get('alias')
    duration = int(request.args.get('select-duration')
        or request.args.get('duration') or app.config['DEFAULT_DURATION'])

    # check duplicates
    if get_current_url(alias) is not None:
        return render_template(
            'error.html',
            msg = 'The alias you chose is unavailable. Please try another one.'
        ), 400

    res = make_response(render_template(
        'created-link.html',
        original_url = original_url,
        alias = alias,
        duration = '%d minutes' % duration
    ))

    # set cookie
    cookie_id = request.cookies.get('id')
    if not cookie_id:
        (cookie_id, cookie_expires) = add_cookie()
        res.set_cookie('id', cookie_id, expires = cookie_expires)

    add_link(alias, original_url, duration, cookie_id)
    return res

# error redirect
@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        'error.html',
        msg = 'Page not found!'
    ), 404

if __name__ == '__main__':
    sched_clean_db()
    if '-init-db' in sys.argv:
        init_db()
    app.run(debug = True)
