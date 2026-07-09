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

def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")

    os.makedirs(os.path.join(os.path.dirname(__file__), "instance"), exist_ok=True)
    db.init_app(app)

    lm = LoginManager()
    lm.login_view = "login"
    lm.login_message_category = "warning"
    lm.init_app(app)

    @lm.user_loader
    def load_user(uid):
        return db.session.get(User, int(uid))

    @app.context_processor
    def inject_globals():
        return dict(
            APP_NAME=app.config["APP_NAME"],
            APP_SHORT=app.config.get("APP_SHORT", "SAJF"),
            TEAM=app.config["TEAM"],
            api_configured=bool(os.environ.get("JSEARCH_API_KEY", "").strip()),
        )
    @app.route("/signup", methods=["GET", "POST"])
    def signup():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            email    = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            confirm  = request.form.get("confirm", "")
            errors = []
            if len(username) < 3:          errors.append("Username must be at least 3 characters.")
            if not EMAIL_RE.match(email):  errors.append("Enter a valid email address.")
            if len(password) < 8:          errors.append("Password must be at least 8 characters.")
            if password != confirm:         errors.append("Passwords do not match.")
            if User.query.filter_by(email=email).first():    errors.append("Email already registered.")
            if User.query.filter_by(username=username).first(): errors.append("Username already taken.")
            if errors:
                for e in errors: flash(e, "danger")
                return render_template("signup.html", username=username, email=email)
            u = User(username=username, email=email)
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
            flash("Account created — please sign in.", "success")
            return redirect(url_for("login"))
        return render_template("signup.html")
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            email    = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            user     = User.query.filter_by(email=email).first()
            if user and user.check_password(password):
                login_user(user)
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(request.args.get("next") or url_for("dashboard"))
            flash("Incorrect email or password.", "danger")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "success")
        return redirect(url_for("login"))
    @app.route("/")
    def landing():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        return render_template("landing.html")

    @app.route("/dashboard")
    @login_required
    def dashboard():
        recent = (SearchLog.query.filter_by(user_id=current_user.id)
                  .order_by(SearchLog.created_at.desc()).limit(5).all())
        return render_template(
            "dashboard.html",
            countries=COUNTRIES, categories=CATEGORIES,
            windows=WINDOW_LABELS, default_window=DEFAULT_WINDOW,
            custom_window_label=CUSTOM_WINDOW_LABEL,
            min_custom_minutes=MIN_CUSTOM_MINUTES,
            max_custom_minutes=MAX_CUSTOM_MINUTES,
            recent=recent,
        )

    @app.route("/search", methods=["POST"])
    @login_required
    def search():
        country  = request.form.get("country",  "").strip()
        city     = request.form.get("region",   "").strip()
        category = request.form.get("category", "").strip()

        if not country or not category:
            flash("Please select a country and job category.", "danger")
            return redirect(url_for("dashboard"))

        try:
            window_secs, window_label = _resolve_window(request.form)
        except ValueError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("dashboard"))

        location = ", ".join(p for p in [city, country] if p)

        try:
            jobs, status = scrapers.aggregate(
                query=category, location=location,
                window_seconds=window_secs,
                timeout=app.config.get("REQUEST_TIMEOUT", 15),
            )
        except Exception:
            app.logger.exception("search: aggregate failed")
            flash("Something went wrong. Please try again.", "danger")
            return redirect(url_for("dashboard"))

        try:
            db.session.add(SearchLog(
                user_id=current_user.id, region=location,
                category=category, results_count=len(jobs),
            ))
            db.session.commit()
        except Exception:
            db.session.rollback()

        return render_template(
            "results.html", jobs=jobs, status=status,
            region=location, category=category, window_label=window_label,
        )
