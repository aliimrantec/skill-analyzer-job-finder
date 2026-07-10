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
    Initialize the SQLite database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # Create jobs table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            company TEXT NOT NULL,
            location TEXT,
            job_url TEXT,
            posted_time TEXT
        )
    """)

    connection.commit()
    connection.close()

    print("Database initialized successfully.")


def job_exists(title, company):
    """
    Check if a job already exists in the database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM jobs
        WHERE title = ? AND company = ?
    """, (title, company))

    job = cursor.fetchone()

    connection.close()

    return job is not None


def save_job(title, company, location, job_url, posted_time):
    """
    Save a job into the SQLite database.
    """

    if job_exists(title, company):
        print("Job already exists.")
        return

    connection = get_connection()
    cursor = connection.cursor()

    
def add_user(username, email, password):
    """
    Save a new user into the database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users (username, email, password)
        VALUES (?, ?, ?)
    """, (username, email, password))

    connection.commit()
    connection.close()








def get_all_jobs():
    """
    Return all jobs from the database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM jobs")

    jobs = cursor.fetchall()

    connection.close()

    return jobs



def get_jobs_by_company(company):
    """
    Return all jobs for a specific company.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM jobs
        WHERE company = ?
    """, (company,))

    jobs = cursor.fetchall()

    connection.close()

    return jobs

def get_user_by_email(email):
    """
    Return one user by email.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    return user


def get_all_users():
    """
    Return all users from the database.
    """

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM users")

    users = cursor.fetchall()

    connection.close()

    return users


if __name__ == "__main__":
    initialize_database()