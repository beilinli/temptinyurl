import sqlite3

con = sqlite3.connect('database.db')
cur = con.cursor()

cur.execute('CREATE TABLE links (alias TEXT, url TEXT, expires TIMESTAMP)')

con.close()
