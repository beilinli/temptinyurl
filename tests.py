import sqlite3, os, unittest, tempfile
from app import app, init_db

class AppTest(unittest.TestCase):
    def setUp(self):
        self.db_fd, app.config['DB_NAME'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        with app.app_context():
            init_db()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DB_NAME'])

    def test_init_db(self):
        con = sqlite3.connect(app.config['DB_NAME'])
        cur = con.cursor()
        self.assertIsNone(cur.execute('select * from links').fetchone())
        con.close()

if __name__ == '__main__':
    unittest.main()
