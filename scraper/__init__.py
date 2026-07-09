"""
scrapers/__init__.py — JSearch API only. No scrapers.
Makes ONE API call per search (saves requests).
Returns top 10 jobs sorted newest first.
"""
from __future__ import annotations

import logging
import os
import requests
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Optional

log = logging.getLogger("scrapers")

API_URL = "https://jsearch.p.rapidapi.com/search"
TOP_N   = 10


# ── Job model ────────────────────────────────────────────────────────────────
@dataclass
class Job:
    title:     str
    company:   str
    location:  str
    url:       str
    source:    str
    posted_at: Optional[datetime] = None

    @property
    def posted_display(self) -> str:
        if not self.posted_at:
            return "Recently"
        delta = datetime.now(timezone.utc) - self.posted_at
        mins  = int(delta.total_seconds() // 60)
        if mins < 1:   return "Just now"
        if mins < 60:  return f"{mins} min ago"
        if mins < 1440: return f"{mins // 60} hr ago"
        return f"{mins // 1440} day(s) ago"


# ── Source status ─────────────────────────────────────────────────────────────
class SourceStatus:
    __slots__ = ("state", "shown", "detail")
    def __init__(self, state="ok", detail=""):
        self.state  = state
        self.shown  = 0
        self.detail = detail
    def label(self) -> str:
        if self.state == "ok":      return f"{self.shown} job{'s' if self.shown != 1 else ''} shown"
        if self.state == "blocked": return "rate-limited / blocked"
        if self.state == "timeout": return "timed out"
        return f"error{f': {self.detail}' if self.detail else ''}"
    def __str__(self): return self.label()


# ── Helpers ───────────────────────────────────────────────────────────────────
def _api_key() -> str:
    return os.environ.get("JSEARCH_API_KEY", "").strip()


def _date_posted(window_seconds: int) -> str:
    if window_seconds <= 86_400:  return "today"
    if window_seconds <= 259_200: return "3days"
    if window_seconds <= 604_800: return "week"
    return "month"


def _parse_iso(value) -> Optional[datetime]:
    if not value: return None
    try:
        txt = str(value).strip().replace("Z", "+00:00")
        dt  = datetime.fromisoformat(txt)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


# ── Main aggregate function ───────────────────────────────────────────────────
def aggregate(query: str, location: str, window_seconds: int = 9000, timeout: int = 15):
    """
    Single JSearch API call → top 10 jobs sorted newest first.
    Returns (jobs, status_dict).
    """
    key = _api_key()
    if not key:
        st = SourceStatus("error", "API key not set")
        return [], {"JSearch": st}

    params = {
        "query":            f"{query} in {location}" if location else query,
        "page":             "1",
        "num_pages":        "2",   # 2 pages ≈ 20 raw results → we keep top 10
        "date_posted":      _date_posted(window_seconds),
        "employment_types": "FULLTIME,CONTRACTOR,PARTTIME",
        "language":         "en",
    }

    try:
        resp = requests.get(
            API_URL,
            headers={"X-RapidAPI-Key": key, "X-RapidAPI-Host": "jsearch.p.rapidapi.com"},
            params=params,
            timeout=timeout,
        )
    except requests.Timeout:
        return [], {"JSearch": SourceStatus("timeout")}
    except Exception as exc:
        return [], {"JSearch": SourceStatus("error", str(exc))}

    if resp.status_code in (401, 403):
        return [], {"JSearch": SourceStatus("blocked", f"HTTP {resp.status_code} — check API key")}
    if resp.status_code == 429:
        return [], {"JSearch": SourceStatus("blocked", "rate-limited (429)")}
    if resp.status_code != 200:
        return [], {"JSearch": SourceStatus("error", f"HTTP {resp.status_code}")}

    try:
        body = resp.json()
    except Exception:
        return [], {"JSearch": SourceStatus("error", "invalid JSON")}

    raw = body.get("data") or []
    now = datetime.now(timezone.utc)

    jobs: list[Job] = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        title    = (item.get("job_title") or "").strip()
        company  = (item.get("employer_name") or "").strip()
        city     = (item.get("job_city") or "").strip()
        country  = (item.get("job_country") or "").strip()
        loc      = ", ".join(p for p in [city, country] if p) or location or "—"
        url      = (item.get("job_apply_link") or item.get("job_google_link") or "").strip()
        publisher= (item.get("job_publisher") or "").strip()
        pub_raw  = item.get("job_posted_at_datetime_utc") or ""

        if not title or not url:
            continue

        posted_at = _parse_iso(pub_raw)

        # Recency filter
        if posted_at:
            age = (now - posted_at).total_seconds()
            if age < 0 or age > window_seconds:
                continue

        jobs.append(Job(
            title=title,
            company=company,
            location=loc,
            url=url,
            source=publisher or "JSearch",
            posted_at=posted_at,
        ))

    # Deduplicate
    seen, unique = set(), []
    for j in jobs:
        key_ = (j.title.lower(), j.company.lower())
        if key_ not in seen:
            seen.add(key_)
            unique.append(j)

    # Sort newest first
    _min = datetime.min.replace(tzinfo=timezone.utc)
    unique.sort(key=lambda j: j.posted_at or _min, reverse=True)
    unique = unique[:TOP_N]

    st = SourceStatus("ok")
    st.shown = len(unique)
    log.info("JSearch: %d jobs returned for '%s'", len(unique), query)
    return unique, {"JSearch": st}
