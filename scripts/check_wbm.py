#!/usr/bin/env python3
"""
Checks the WBM Berlin apartment listings page for new offers and sends a
Telegram notification as soon as a new one appears.

State (the list of listing URLs seen so far) is stored in listings.json
at the repo root, so it persists between GitHub Actions runs.
"""

import json
import os
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

URL = "https://www.wbm.de/wohnungen-berlin/angebote/"
STATE_FILE = Path(__file__).resolve().parent.parent / "listings.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HEADERS = {
    # A normal browser-like User-Agent; be a polite, low-frequency visitor.
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_listings():
    """Fetch the WBM offers page and return a dict of {url: title}."""
    resp = requests.get(URL, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    listings = {}
    # Each listing detail link looks like:
    # /wohnungen-berlin/angebote/details/<slug>/
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/wohnungen-berlin/angebote/details/" in href:
            full_url = href if href.startswith("http") else f"https://www.wbm.de{href}"
            title = a.get_text(strip=True)
            if title:  # skip empty "Ansehen"/"Zum Exposé" duplicates without text
                listings[full_url] = title
            elif full_url not in listings:
                listings[full_url] = ""  # placeholder, may get overwritten below

    # Fill in any placeholder titles from a later pass over the same link
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/wohnungen-berlin/angebote/details/" in href:
            full_url = href if href.startswith("http") else f"https://www.wbm.de{href}"
            text = a.get_text(strip=True)
            if text and not listings.get(full_url):
                listings[full_url] = text

    return listings


def load_previous_state():
    if STATE_FILE.exists():
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_state(listings):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(listings, f, ensure_ascii=False, indent=2, sort_keys=True)


def send_telegram_message(text):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set — skipping notification.", file=sys.stderr)
        return
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    resp = requests.post(api_url, data=payload, timeout=15)
    if not resp.ok:
        print(f"Telegram send failed: {resp.status_code} {resp.text}", file=sys.stderr)


def main():
    previous = load_previous_state()
    current = fetch_listings()

    new_urls = [u for u in current if u not in previous]

    if not previous:
        # First ever run: just save the baseline, don't spam notifications
        # for every currently-existing listing.
        print(f"Initial run — saving baseline of {len(current)} listings.")
        save_state(current)
        return

    if new_urls:
        print(f"Found {len(new_urls)} new listing(s)!")
        for url in new_urls:
            title = current[url] or "New WBM listing"
            message = f"🏠 <b>New WBM listing!</b>\n{title}\n{url}"
            send_telegram_message(message)
            time.sleep(1)  # be gentle with Telegram's API too
    else:
        print("No new listings.")

    save_state(current)


if __name__ == "__main__":
    main()
