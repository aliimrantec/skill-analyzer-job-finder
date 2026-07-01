import sqlite3
from config import Config


def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(Config.DATABASE_PATH)
    return connection


def initialize_database():
    """
    Initialize SQLite database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()

    print("User table created successfully.")


if __name__ == "__main__":
    initialize_database()