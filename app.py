from flask import Flask, render_template, request, session, url_for

app = Flask(__name__)

app.secret_key = "%\xde\xe0\x1bjT\x9bS\xe9\x9at'\xf6\x9f'^3\x10F\xf3\x8f7\xadD"

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/create')
def created_tiny():
	return render_template(
		'created-link.html',
		original_url = request.args['url'],
		alias = request.args['alias'],
		duration = 'undetermined'
	)

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html'), 404

if __name__ == '__main__':
	app.run(debug = True)
