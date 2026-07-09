# Skill Analyzer and Job Finder — v7

Searches **LinkedIn**, **Indeed**, and **Rozee.pk** simultaneously for the
top 10 most-recent jobs matching your chosen skill category.

---

## How sources are accessed

| Source | Official API? | What we use |
|---|---|---|
| LinkedIn | ❌ Partner-only ($10k+/yr) | JSearch API (indexes LinkedIn via Google for Jobs) |
| Indeed | ❌ Publisher API deprecated 2023 | JSearch API (indexes Indeed via Google for Jobs) |
| Rozee.pk | ❌ No public API | JSearch API + direct HTML scraper fallback |

**JSearch by OpenWeb Ninja** is the only legitimate free API that aggregates
all three sources. It pulls live data from Google for Jobs, which indexes
LinkedIn, Indeed, Glassdoor, Rozee.pk, and 100+ more boards.

---

## Quick start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Get a free JSearch API key (recommended, no credit card)
#    https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
#    Free plan: 200 requests/month

# 3. Set your key
export JSEARCH_API_KEY="your_rapidapi_key_here"

# 4. Run
python app.py
```

Open http://127.0.0.1:5000

---

## Environment variables

| Variable | Required | Description |
|---|---|---|
| `JSEARCH_API_KEY` | **Recommended** | RapidAPI key for JSearch. Without it, falls back to direct HTML scraping which can be blocked. |
| `JOBRECON_SECRET_KEY` | Production | Flask session signing key |
| `JOBRECON_DATABASE_URL` | Optional | Override SQLite (e.g. Postgres URL) |
| `SCRAPER_PROXY` | Optional | HTTP proxy for scraper fallbacks |

Copy `.env.example` → `.env` and fill in your values.

---

## Architecture

```
User → Flask app → scrapers/aggregate()
                        ├── LinkedIn  → JSearch API (via_linkedin query)  → fallback: HTML scraper
                        ├── Indeed    → JSearch API (via_indeed query)    → fallback: HTML scraper
                        └── Rozee.pk  → JSearch API (Pakistan query)      → fallback: HTML scraper + Mustakbil
                   ↓
              Global top-10 (deduplicated, sorted by timestamp)
```

The scraper fallbacks use the v6 HTML parsers with JSON-embed extraction.
They activate automatically when:
- `JSEARCH_API_KEY` is not set
- JSearch is rate-limited or returns an error for a specific source

---

## Results page

- **Source status bar** — shows each source as `api` (green) or `scraper`,
  with blocked/timeout indicators
- **Rank numbers** — 1 to 10
- **Timestamps** — highlighted green when the job is very fresh
- **Top 10 badge** — confirms the global cap is applied

---

## Developed by Arham & Ali — Open-Source Software Development Project
