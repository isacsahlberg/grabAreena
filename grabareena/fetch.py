from datetime import date
from importlib.metadata import version, PackageNotFoundError
import requests

API_BASE = "https://areena.api.yle.fi/v1/ui/schedules/yle-klassinen/{day}.json"
PARAMS = {
    "app_id": "areena-web-items",
    "app_key": "wlTs5D9OjIdeS9krPzRQR4I1PYVzoazN",
    "language": "fi",
    "v": 10,
    "limit": 100,
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
