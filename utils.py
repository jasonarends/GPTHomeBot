import sqlite3
import os
from langchain.text_splitter import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter, Document
from icecream import ic


class Utils:
    @staticmethod
    def split_messages(message, limit=2000, overlap=20, headers_to_split_on=None):
        if len(message) <= limit:
            return [message]

        # Initialize markdown header splitter
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on or [
            ("#", "Header 1"),
            ("##", "Header 2"),
        ])

        # Split markdown document by headers
        md_header_splits = markdown_splitter.split_text(message)

        # Initialize recursive character text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=limit, 
            chunk_overlap=overlap
        )

        # Split each markdown section further if necessary
        splits = []
        for section in md_header_splits:
            # Extract text if section is a Document
            text_to_split = section.page_content if isinstance(section, Document) else section

            # Ensure text_to_split is a string before splitting
            if isinstance(text_to_split, str):
                section_splits = text_splitter.split_text(text_to_split)
                splits.extend(section_splits)

        return splits

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
