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
    initializing the sqlite database ...
    """
    
    connection=get_connection()
    print("database initialized successfully")
    connection.close()
    
if __name__ == "__main__":
    initialize_database()
    