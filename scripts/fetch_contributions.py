#!/usr/bin/env python3
"""Fetch DiaskinCode's public contribution calendar without an API token."""

import argparse
import datetime as dt
import json
import os
import re
import urllib.request
from html.parser import HTMLParser

USERNAME = os.environ.get("GH_PROFILE_USER", "DiaskinCode")
URL = f"https://github.com/users/{USERNAME}/contributions"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "data", "contributions.json")


class ContributionParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.cells = {}
        self.tooltips = {}
        self.current_tooltip = None
        self.current_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "").split()
        if tag == "td" and "ContributionCalendar-day" in classes:
            cell_id = attrs.get("id")
            date = attrs.get("data-date")
            if cell_id and date:
                self.cells[cell_id] = date
        elif tag == "tool-tip" and attrs.get("for"):
            self.current_tooltip = attrs["for"]
            self.current_text = []

    def handle_data(self, data):
        if self.current_tooltip:
            self.current_text.append(data)

    def handle_endtag(self, tag):
        if tag == "tool-tip" and self.current_tooltip:
            self.tooltips[self.current_tooltip] = "".join(self.current_text).strip()
            self.current_tooltip = None
            self.current_text = []


def read_html(path=None):
    if path:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    request = urllib.request.Request(URL, headers={"User-Agent": "profile-readme-bot/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_days(markup):
    parser = ContributionParser()
    parser.feed(markup)
    days = []
    for cell_id, date in parser.cells.items():
        label = parser.tooltips.get(cell_id, "")
        match = re.match(r"([\d,]+) contribution", label, re.I)
        count = int(match.group(1).replace(",", "")) if match else 0
        days.append({"date": date, "count": count})
    days.sort(key=lambda item: item["date"])
    if not days:
        raise RuntimeError("GitHub returned no contribution cells")
    return days


def streaks(days):
    longest = current = run = 0
    longest_start = longest_end = run_start = None
    for item in days:
        if item["count"]:
            if run == 0:
                run_start = item["date"]
            run += 1
            if run > longest:
                longest, longest_start, longest_end = run, run_start, item["date"]
        else:
            run = 0
    index = len(days) - 1
    if days[index]["count"] == 0:
        index -= 1
    current_end = days[index]["date"] if index >= 0 else None
    while index >= 0 and days[index]["count"]:
        current += 1
        index -= 1
    current_start = days[index + 1]["date"] if current else None
    return (
        {"length": current, "start": current_start, "end": current_end if current else None},
        {"length": longest, "start": longest_start, "end": longest_end},
    )


def build_data(days):
    current, longest = streaks(days)
    total = sum(item["count"] for item in days)
    active = sum(bool(item["count"]) for item in days)
    best = max(days, key=lambda item: item["count"])
    return {
        "username": USERNAME,
        "generated_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "range": {"start": days[0]["date"], "end": days[-1]["date"]},
        "total_contributions": total,
        "active_days": active,
        "current_streak": current,
        "longest_streak": longest,
        "best_day": best,
        "days": days,
    }


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--input-html", help="Use a saved calendar page instead of downloading")
    args = cli.parse_args()
    data = build_data(parse_days(read_html(args.input_html)))
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    print(f"wrote {OUT_PATH}: {data['total_contributions']} contributions")
