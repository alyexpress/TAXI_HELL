import sqlite3

class Database:
    def __init__(self, filename):
        self.db = sqlite3.connect(filename)
        self.cur = self.db.cursor()

    def close(self):
        self.db.close()