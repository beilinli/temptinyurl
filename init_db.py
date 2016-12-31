import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute('CREATE TABLE links (alias TEXT, url TEXT, duration INTEGER,' \
    'created TIMESTAMP DEFAULT CURRENT_TIMESTAMP)')

con.close()
