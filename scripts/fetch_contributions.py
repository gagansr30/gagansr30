"""
fetch_contributions.py

Fetches the public GitHub contribution calendar (no token / no GraphQL needed)
from https://github.com/users/<username>/contributions and writes
data/contributions.json with the raw day-by-day data plus derived stats
(current streak, longest streak, best day, monthly totals).
"""
import json
import os
import re
from datetime import datetime

import requests
from bs4 import BeautifulSoup

USERNAME = os.environ.get("GITHUB_PROFILE_USERNAME", "gagansr30")
URL = f"https://github.com/users/{USERNAME}/contributions"
OUT_PATH = os.path.join("data", "contributions.json")

ROWS = 7   # Sun-Sat
COLS = 53  # weeks


def parse_count(tooltip_text):
    if not tooltip_text:
        return 0
    if tooltip_text.startswith("No contributions"):
        return 0
    m = re.match(r"^(\d+)\s+contribution", tooltip_text.strip())
    return int(m.group(1)) if m else 0


def fetch_days():
    resp = requests.get(URL, headers={"User-Agent": "profile-readme-bot"}, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # map tool-tip id -> tooltip text (real contribution counts live here)
    tip_map = {}
    for tip in soup.select("tool-tip"):
        for_id = tip.get("for")
        if for_id:
            tip_map[for_id] = tip.get_text(strip=True)

    days = []
    for cell in soup.select("td.ContributionCalendar-day"):
        cell_id = cell.get("id")
        date = cell.get("data-date")
        level = int(cell.get("data-level", "0") or 0)
        tooltip = tip_map.get(cell_id, "")
        count = parse_count(tooltip)
        days.append({"date": date, "level": level, "count": count})

    return days


def compute_stats(days):
    by_date = sorted(days, key=lambda d: d["date"])
    total = sum(d["count"] for d in by_date)

    longest = 0
    run = 0
    for d in by_date:
        if d["count"] > 0:
            run += 1
            longest = max(longest, run)
        else:
            run = 0

    current = 0
    for d in reversed(by_date):
        if d["count"] > 0:
            current += 1
        else:
            break

    best = max(by_date, key=lambda d: d["count"]) if by_date else None

    monthly = {}
    for d in by_date:
        if not d["date"]:
            continue
        month_key = d["date"][:7]  # YYYY-MM
        monthly[month_key] = monthly.get(month_key, 0) + d["count"]

    return {
        "total": total,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "monthly_totals": monthly,
    }


def build_grid(days):
    # GitHub renders the calendar's DOM in row-major order (all Sundays,
    # then all Mondays, ...), so flat[row * COLS + col] gives day (col, row).
    grid = [[None] * ROWS for _ in range(COLS)]
    for i, day in enumerate(days):
        row = i // COLS
        col = i % COLS
        if col < COLS and row < ROWS:
            grid[col][row] = day
    return grid


def main():
    days = fetch_days()
    if not days:
        raise SystemExit("No contribution cells found - GitHub markup may have changed")

    stats = compute_stats(days)
    grid = build_grid(days)

    os.makedirs("data", exist_ok=True)
    payload = {
        "username": USERNAME,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "days": days,
        "grid": grid,
        "stats": stats,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    print(f"Wrote {OUT_PATH}: {len(days)} days, {stats['total']} total contributions")


if __name__ == "__main__":
    main()
