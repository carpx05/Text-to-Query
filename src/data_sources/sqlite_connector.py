import sqlite3
import json
from config import Config

class SQLiteConnector:
    def __init__(self):
        self.conn = None
        self.cursor = None

    def connect(self):
        self.conn = sqlite3.connect(Config.SQLITE_CACHE_FILE)
        self.cursor = self.conn.cursor()
        self._create_table()

    def _create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS rag_results
                               (id INTEGER PRIMARY KEY, query TEXT, answer TEXT, sources TEXT)''')
        self.conn.commit()

    def get_result(self, query):
        self.cursor.execute("SELECT answer, sources FROM rag_results WHERE query = ?", (query,))
        result = self.cursor.fetchone()
        if result:
            return result[0], json.loads(result[1])
        return None, None

    def store_result(self, query, answer, sources):
        self.cursor.execute("INSERT INTO rag_results (query, answer, sources) VALUES (?, ?, ?)",
                            (query, answer, json.dumps(sources)))
        self.conn.commit()

    def close(self):
        if self.conn:
            self.conn.close()