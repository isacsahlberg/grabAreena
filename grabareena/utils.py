from datetime import date, datetime, timedelta
from termcolor import colored
import re


DEFAULT_PATTERNS = ["Bach", "Mozart", "Schumann"]

def parse_patterns(args_pattern) -> list[str]:
    if not args_pattern:                 # if no -p given, use defaults
        return DEFAULT_PATTERNS.copy()
    patterns = []
    for arg in args_pattern:
        patterns.extend(s.strip() for s in arg.split(",") if s.strip())
    return patterns


def resolve_date(date_str: str | None, tomorrow: bool) -> date:
    if date_str:
        # If user gave an explicit date, ignore --tomorrow, print a warning if that flag was also used
        if tomorrow:
            print(f"Defaulting to the set 'date': {date_str}")
        return date.fromisoformat(date_str)
    base = date.today()
    return base + timedelta(days=1) if tomorrow else base
