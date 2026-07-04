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
CATEGORIES = {
    "Programming Languages": [
        "Python Developer","Java Developer","JavaScript Developer",
        "TypeScript Developer","C Developer","C++ Developer",
        "C# Developer","PHP Developer","Ruby Developer",
        "Go Developer","Rust Developer","Kotlin Developer","Swift Developer",
    ],
    "Web Development": [
        "Frontend Developer","Backend Developer","Full Stack Developer",
        "Web Developer","React Developer","Angular Developer",
        "Vue.js Developer","Node.js Developer","WordPress Developer",
        "Django Developer","Laravel Developer",
    ],
    "Mobile": [
        "Android Developer","iOS Developer","Flutter Developer",
        "React Native Developer","Mobile App Developer",
    ],
    "Data & AI": [
        "Data Scientist","Data Analyst","Machine Learning Engineer",
        "AI Engineer","Data Engineer","Business Intelligence Analyst",
    ],
    "Infrastructure & Security": [
        "DevOps Engineer","Cloud Engineer","AWS Engineer",
        "Cybersecurity Engineer","Network Engineer","System Administrator",
        "Database Administrator","Linux Administrator",
    ],
    "Other Tech": [
        "Software Engineer","QA Engineer","UI/UX Designer",
        "Product Manager","Blockchain Developer","Embedded Systems Engineer",
    ],
}
def _resolve_window(form):
    label = form.get("window", DEFAULT_WINDOW)
    if label == CUSTOM_WINDOW_LABEL:
        raw = (form.get("custom_minutes") or "").strip()
        if not raw:
            raise ValueError("Please enter the number of minutes.")
        try:
            minutes = int(float(raw))
        except (ValueError, TypeError):
            raise ValueError("Custom window must be a whole number.")
        if minutes <= 0:
            raise ValueError("Time window must be at least 1 minute.")
        minutes = min(minutes, MAX_CUSTOM_MINUTES)
        return minutes * 60, f"Last {minutes} min"
    seconds = WINDOWS_MAP.get(label, WINDOWS_MAP[DEFAULT_WINDOW])
    return seconds, label

