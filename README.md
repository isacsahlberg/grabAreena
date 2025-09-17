### grabAreena — JSON rewrite (new-data-backend)

Working rewrite that uses Yle’s JSON schedule endpoint, replacing the old HTML scraper.

---


### Requirements
- Python 3.11+
- [uv](https://github.com/astral-sh/uv)


### Setup
1) Clone and switch branch:
```bash
git clone https://github.com/isacsahlberg/grabAreena.git
cd grabAreena
git checkout new-data-backend
```
2) Install dependencies with uv:
```bash
uv sync
```
This creates a `.venv` and adds/installs dependencies like `requests`, `termcolor`.


### Project structure
```bash
grabAreena/
├─ main.py
├─ pyproject.toml
└─ grabareena/
   ├─ __init__.py
   ├─ cli.py
   ├─ cache.py
   ├─ parsing.py
   ├─ printing.py
   ├─ models.py
   └─ utils.py
```


### What it does
- Fetches the Yle Klassinen daily schedule (JSON) and caches it to: `~/.cache/grabareena/yle-klassinen-YYYY-MM-DD.json`
- Parses program “pieces” (timestamped items inside a program)
- Prints a variety of info, depending on user flags:
  - program list (headers only)
  - all pieces (full schedule, grouped by program)
  - pattern search, grouped by pattern (matching is case-insensitive)
- Times crossing midnight get a leading `+`


### Usage
```bash
uv run python main.py [OPTIONS]

# alternatively
source .venv/bin/activate
python main.py [OPTIONS]
```


### Optional flags
```bash
-d, --date YYYY-MM-DD   date (default: today)
-t, --tomorrow          use tomorrow (ignored if --date is given)
-r, --refresh           bypass cache (force fetch & save)
-p, --pattern PAT       may repeat or use commas (e.g., -p Bach -p Mozart  or  -p "Bach, Mozart")
-P, --programs          program headers only
-a, --all               all pieces (if -p is present, highlights inline)
```
If you skip the flags altogether, the date defaults to today, and the pattern to a pre-defined set of composers.


### Recommended: You can run this tool from anywhere using uv:
```bash
uv run --project ~/path/to/repo python ~/path/to/repo/main.py
```
in particular, the easiest way to have this tool easily available is using an alias on the full `uv` command:
```bash
alias grabAreena='uv run --project ~/path/to/repo python -m ~/path/to/repo/main.py'
```


### Usage examples (assuming you use the above alias)
```bash
# Default date is today
grabAreena                          # find matches for default pattern arguments, today
grabAreena -t                       # find matches for default pattern arguments, tomorrow
# The simple flags can be combined
grabAreena -a                       # print the entire schedule for today
grabAreena -at                      # print the entire schedule for tomorrow
# Pattern flags can be compounded
grabAreena -p "Bach, Mozart"        # find matches for specific composers (or any program substrings)
grabAreena -p "Bach" -p "Mozart"    # same
```
Combining many just looks like this
```bash
grabAreena --date 2025-12-24 --all --pattern "Bach"
```
Attempting to access data for dates more than ±3 days away from today will probably fail, you'll just get something like: `{"developerMessage":"Specified date is beyond current program guide scope"`. One week into the past seems to be working fine.


### Notes / Implementation details
- Titles/descriptions are printed “as is” (punctuation preserved).
- Times that cross midnight are marked with a leading “+” on the following day.
- Cache writes are atomic (tmp+replace). Corrupt/missing cache -> refetch with -r.
- Minimal error handling by design; failures should be obvious and easy to fix.
- The source data can have typos (yes, really), so don't judge this tool too harshly.


### TODO
- Optional diacritic-insensitive matching (e.g., Dvořák ≈ Dvorak).
