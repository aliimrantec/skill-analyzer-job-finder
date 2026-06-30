"""
Configuration settings for Skill Analyzer & Job Finder.
"""

import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
class Config:
    # Flask secret key
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    # SQLite database name
    DATABASE_NAME = "skill_analyzer.db"

    # Full database path
    DATABASE_PATH = os.path.join(BASE_DIR, DATABASE_NAME)
    
    # Search settings
    SEARCH_WINDOW_MINUTES = 120
    MAX_RESULTS = 50

    # Network timeout
    REQUEST_TIMEOUT = 10

    # Application information
    APP_NAME = "Skill Analyzer & Job Finder"