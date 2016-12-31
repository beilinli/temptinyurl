from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

# app info

app = Flask(__name__)
app.secret_key = "%\xde\xe0\x1bjT\x9bS\xe9\x9at'\xf6\x9f'^3\x10F\xf3\x8f7\xadD"

DB_NAME = 'database.db'

# views

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/link/<alias>')
def link(alias):
	con = sqlite3.connect(DB_NAME)
	cur = con.cursor()

	cur.execute('SELECT url FROM links WHERE alias = ?', (alias,))
	url = cur.fetchone()
	con.close()

	if url is None:
		return render_template(
			'error.html',
			msg = 'There is no tiny link with that alias. ' \
			'Please check the URL or create a link on the homepage.'
		), 404

	return redirect(url[0])

@app.route('/create')
def create_tiny():
	con = sqlite3.connect(DB_NAME)
	cur = con.cursor()

	original_url = request.args.get('url')
	alias = request.args.get('alias')

	# check duplicates
	cur.execute('SELECT * FROM links WHERE alias = ?', (alias,))
	if (cur.fetchone() is not None):
		return render_template(
			'error.html',
			msg = 'The alias you\'ve chosen is not available. Please try another one.'
		), 400

	# create tiny URL
	cur.execute('INSERT INTO links (alias, url) VALUES (?, ?)', (alias, original_url))

	con.commit()
	con.close()

	return render_template(
		'created-link.html',
		original_url = original_url,
		alias = alias,
		duration = 'undetermined'
	)

@app.errorhandler(404)
def page_not_found(e):
	return render_template(
		'error.html',
		msg = 'Page not found!'
	), 404

if __name__ == '__main__':
	app.run(debug = True)
