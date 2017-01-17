import sqlite3
import os.path


class OP1DB:
    def __init__(self):
        self.conn = None

    def __del__(self):
        if self.conn:
            self.conn.close()

    def open(self, path):
        path = os.path.abspath(path)
        if not os.path.exists(path):
            raise FileNotFoundError("Database file doesn't exist.")
        self.conn = sqlite3.connect(path)

    def commit(self):
        self.conn.commit()
        return True

    # TODO: Don't overwrite row if id exists
    def enable_filter(self):
        # Make sure it's not already enabled
        out = self.conn.execute('SELECT * FROM fx_types WHERE type = \'filter\'')
        results = out.fetchall()
        if results:
            return False
        new_row = (2, 'filter', '[8000, 8000, 18000, 18000, 8000, 8000, 8000, 8000]')
        self.conn.execute('INSERT INTO fx_types VALUES (?,?,?)', new_row)
        return True

    def enable_iter(self):
        # Make sure it's not already enabled
        out = self.conn.execute('SELECT * FROM synth_types WHERE type = \'iter\'')
        results = out.fetchall()
        if results:
            return False
        new_row = (11, 'iter', '[1516, 16704, 0, 15168, 0, 0, 0, 0]')
        self.conn.execute('INSERT INTO synth_types VALUES (?,?,?)', new_row)
        return True
