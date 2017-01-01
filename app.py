from flask import Flask, render_template, request, redirect, session, url_for
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit, sqlite3, time

# app info

app = Flask(__name__)
app.secret_key = "%\xde\xe0\x1bjT\x9bS\xe9\x9at'\xf6\x9f'^3\x10F\xf3\x8f7\xadD"

DB_NAME = 'database.db'
DEFAULT_DURATION = 30   # minutes
DB_CLEAR_INTERVAL_HRS = 6   # hours

'''
clear old URL info
'''

def clear_db_old():
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute('DELETE FROM links WHERE CURRENT_TIMESTAMP > expires')
    con.commit()
    con.close()

'''
views
'''

@app.route('/')
def index():
	return render_template('index.html')

# utilize short link
@app.route('/link/<alias>')
def link(alias):
	con = sqlite3.connect(DB_NAME)
	cur = con.cursor()

	cur.execute('SELECT url FROM links WHERE alias = ? AND CURRENT_TIMESTAMP < expires', (alias,))
	url = cur.fetchone()
	con.close()

	if url is None:
		return render_template(
			'error.html',
			msg = 'There is no tiny link with that alias. ' \
			'Please check the URL or create a link on the homepage.'
		), 404

	# TODO: check if link is current
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

	print("Duration is %d minutes" % duration)

	# check duplicates
	cur.execute('SELECT * FROM links WHERE alias = ? AND CURRENT_TIMESTAMP < expires', (alias,))

	if (cur.fetchone() is not None):
		return render_template(
			'error.html',
			msg = 'The alias you\'ve chosen is not available. Please try another one.'
		), 400

	# create tiny URL
	cur.execute('INSERT INTO links (alias, url, expires) VALUES (?, ?, ' \
    'DATETIME("now", "+" || ? || " minutes"))', (alias, original_url, duration,))

	con.commit()
	con.close()

	return render_template(
		'created-link.html',
		original_url = original_url,
		alias = alias,
		duration = "%d minutes" % duration
	)

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
    	replace_existing = True)

    # set DB clear process to shutdown with app
	atexit.register(lambda: db_clear_sched.shutdown())

    # start server
	app.run(debug = True)
