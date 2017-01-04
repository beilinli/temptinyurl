from flask import Flask, make_response, render_template, request, redirect, session, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit, sqlite3, time, datetime

# app info

app = Flask(__name__)
app.secret_key = "%\xde\xe0\x1bjT\x9bS\xe9\x9at'\xf6\x9f'^3\x10F\xf3\x8f7\xadD"

DB_NAME = 'database.db'
DEFAULT_DURATION = 30   # minutes
DB_CLEAR_INTERVAL_HRS = 6   # hours
COOKIE_TIME = 1 # days
# NOTE: Chrome cookies expire too early

'''
clear old URL and cookie info
'''

def clear_db_old():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('DELETE FROM links WHERE ? > expires', (datetime.datetime.now(),))
    cur.execute('DELETE FROM cookies WHERE ? > expires', (datetime.datetime.now(),))
    con.commit()
    con.close()

'''
views
'''

@app.route('/')
def index():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('SELECT * from links WHERE cookie_id = ?', (request.cookies.get('id'),))
    links = cur.fetchall()
    con.close()

    return render_template('index.html', links = links)

# utilize short link
@app.route('/link/<alias>')
def link(alias):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    cur.execute('SELECT url FROM links WHERE alias = ? AND ? < expires',
    (alias, datetime.datetime.now(),))
    url = cur.fetchone()

    con.close()

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
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()

    original_url = request.args.get('url')
    alias = request.args.get('alias')
    duration = int(request.args.get('select-duration')
        or request.args.get('duration') or DEFAULT_DURATION) # minutes

    # check duplicates
    cur.execute('SELECT * FROM links WHERE alias = ? AND ? < expires', (alias,
    datetime.datetime.now(),))

    if cur.fetchone() is not None:
        return render_template(
            'error.html',
            msg = 'The alias you chose is unavailable. Please try another one.'
        ), 400

    res = make_response(render_template(
        'created-link.html',
        original_url = original_url,
        alias = alias,
        duration = "%d minutes" % duration
    ))

    # set cookie
    cookie_id = request.cookies.get('id')
    if not cookie_id:
        cookie_expires = datetime.datetime.now() + datetime.timedelta(days
        = COOKIE_TIME)
        cur.execute('INSERT INTO cookies (expires) VALUES (?)', (cookie_expires,))
        cookie_id = str(cur.lastrowid)
        res.set_cookie('id', cookie_id, expires = cookie_expires)

    # create tiny URL
    cur.execute('INSERT INTO links (alias, url, expires, cookie_id) VALUES' \
    '(?, ?, ?, ?)', (alias, original_url, datetime.datetime.now() +
    datetime.timedelta(minutes = duration), cookie_id,))

    con.commit()
    con.close()

    return res

# error redirect
@app.errorhandler(404)
def page_not_found(e):
    return render_template(
        'error.html',
        msg = 'Page not found!'
    ), 404

if __name__ == '__main__':
    # schedule DB cleans every 6 hours
    db_clear_sched = BackgroundScheduler()
    db_clear_sched.start()
    db_clear_sched.add_job(
        func = clear_db_old,
        trigger = IntervalTrigger(hours = DB_CLEAR_INTERVAL_HRS),
        replace_existing = True
    )

    # set DB clear process to shutdown with app
    atexit.register(lambda: db_clear_sched.shutdown())

    # start server
    app.run(debug = True)
