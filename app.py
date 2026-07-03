from __future__ import annotations
import logging
import os
import re
from dotenv import load_dotenv
load_dotenv()  # loads JSEARCH_API_KEY from .env
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user

import scrapers
from config import Config
from models import SearchLog, User, db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

WINDOWS_MAP = {
    "Last 1 hour":    3_600,
    "Last 2.5 hours": 9_000,
    "Last 6 hours":  21_600,
    "Last 24 hours": 86_400,
}
WINDOW_LABELS  = list(WINDOWS_MAP.keys())
DEFAULT_WINDOW = "Last 2.5 hours"
CUSTOM_WINDOW_LABEL = "Custom (minutes)"
MIN_CUSTOM_MINUTES  = 1
MAX_CUSTOM_MINUTES  = 10_080
COUNTRIES = [
    "Pakistan", "United States", "United Kingdom",
    "United Arab Emirates", "Saudi Arabia", "Canada",
    "Australia", "Germany", "India",
]


