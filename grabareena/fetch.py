from datetime import date
from html import unescape
from importlib.metadata import version, PackageNotFoundError
import requests
import re

API_BASE = "https://areena.api.yle.fi/v1/ui/schedules/yle-klassinen/{day}.json"
PARAMS = {
    "app_id": "areena-web-items",
    "app_key": "wlTs5D9OjIdeS9krPzRQR4I1PYVzoazN",
    "language": "fi",
    "v": 10,
    "limit": 100,
    "client": "yle-areena-web",
}


def user_agent():
    try: v = version("grabareena")
    except PackageNotFoundError: v = "dev"
    return f"grabareena/{v} (+https://github.com/isacsahlberg/grabAreena)"

HEADERS = {
    "User-Agent": user_agent(),
    "Accept": "application/json",
}


def fetch_schedule(day: date) -> dict:
    url = API_BASE.format(day=day.isoformat())
    r = requests.get(url, params=PARAMS, headers=HEADERS, timeout=10)
    r.raise_for_status()
    return r.json()


def fetch_headline(url: str) -> str | None:
    """Fetch the editorial headline from a program's Areena page."""
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        r.raise_for_status()
        match = re.search(r'og:title" content="([^"]+)"', r.text)
        if match:
            return unescape(match.group(1).split("|")[0].strip())
    except Exception:
        return None
    return None
