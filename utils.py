import sqlite3
import os

class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = None
        self.initialize_database()

    def initialize_database(self):
        # Create database file if it doesn't exist
        if not os.path.exists(self.db_file):
            open(self.db_file, 'a').close()

        # Connect to the database
        self.conn = sqlite3.connect(self.db_file)

        # Create the table
        self.create_table()

    def create_table(self):
        query = '''CREATE TABLE IF NOT EXISTS user_threads (
                       user_id TEXT PRIMARY KEY,
                       thread_id TEXT
                   )'''
        self.conn.execute(query)
        self.conn.commit()

    def get_thread_id(self, user_id):
        query = 'SELECT thread_id FROM user_threads WHERE user_id = ?'
        cursor = self.conn.execute(query, (user_id,))
        result = cursor.fetchone()
        return result[0] if result else None

    def set_thread_id(self, user_id, thread_id):
        query = 'INSERT OR REPLACE INTO user_threads (user_id, thread_id) VALUES (?, ?)'
        self.conn.execute(query, (user_id, thread_id))
        self.conn.commit()
