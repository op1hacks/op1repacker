import sqlite3
import os.path


class OP1DB:
    def __init__(self):
        self.conn = None
        # New default params for FX that affect the sound as little as possible
        # This avoids sudden changes to the sound when enabling an effect
        # during live performances.
        self.subtle_fx_params = {
            "cwo":       "[0, 0, 0, 0, 0, 0, 0, 0]",
            "delay":     "[8000, 8000, 8000, 0, 0, 0, 0, 0]",
            "filter":    "[7548, 0, 8272, 19572, 8000, 8000, 8000, 8000]",
            "grid":      "[8000, 8000, 18000, 0, 8000, 8000, 8000, 8000]",
            "nitro":     "[64, 0, 10323, 16448, 0, 0, 0, 0]",
            "phone":     "[8000, 8000, 8016, 0, 8000, 8000, 8000, 8000]",
            "punch":     "[6000, 15000, 20000, 0, 8000, 8000, 8000, 8000]",
            "spring":    "[16448, 8560, 9728, 0, 8000, 8000, 8000, 8000]",
        }

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
        new_row = (2, 'filter', '[7548, 0, 8272, 19572, 8000, 8000, 8000, 8000]')
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

    def enable_subtle_fx_defaults(self):
        types = self.get_existing_fx_types()
        for fx_type in types:
            if fx_type in self.subtle_fx_params:
                params = self.subtle_fx_params[fx_type]
                self.set_fx_default_params(fx_type, params)
        return True

    def get_existing_fx_types(self):
        out = self.conn.execute('SELECT type FROM fx_types')
        results = out.fetchall()
        if not results:
            return []

        fx_types = map(lambda row: row[0], results)
        return fx_types

    def set_fx_default_params(self, fx_type, params):
        self.conn.execute('UPDATE fx_types SET default_params=? WHERE type=?', (params, fx_type))

    def synth_preset_folder_exists(self, synth_type):
        # Check if there are any synth presets under the folder synth_type
        out = self.conn.execute('SELECT * FROM synth_presets WHERE folder=?', (synth_type, ))
        results = out.fetchall()
        if results:
            return True
        return False

    def insert_synth_preset(self, patch, folder):
        self.conn.execute('INSERT INTO synth_presets (patch, folder) VALUES (?, ?)', (patch, folder))
        return True
