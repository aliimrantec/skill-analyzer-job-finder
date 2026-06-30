import sqlite3
from config import Config
def get_connection():
    """
    Create and return a connection to the SQLite database.
    """
    connection = sqlite3.connect(Config.DATABASE_PATH)
    return connection
