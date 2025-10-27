### grabAreena

Are you a fan of classical music?
In particular, do you listen to it live on the radio, because you are fed up with lists and bookmarks, and listening to music live keeps you centered in the present?
Are you so lazy that you can't be bothered to search through the day's pieces for your favorite composers to see _when exactly_ you should remember to have the radio on?
And do you listen to it on the Finnish radio? If you answered yes to all of these, you are most likely me, and you should probably stop writing this silliness and do something else.
But nevertheless, _grabAreena_ is for you!

Under the hood, _grabAreena_ retrieves the schedule from Yle Areena's JSON schedule endpoint, caches it locally, and parses programme descriptions into pieces along with useful information.
By default, it outputs only the matching pieces that we are looking for -- use your own `pattern` to match the composer or performer, or just use the default ones.

### Highlights:
- Works for a chosen date, defaults to today
- Fast and polite: responses are cached under `~/.cache/grabareena/...`
- Clean output with start-end times, supports midnight rollover (`+00:30` style)
- Simple pattern matching, supports single and multiple strings
- Additional information available using other flags (see below)

---


### Requirements
- [uv](https://github.com/astral-sh/uv)
- Python 3.13+

(`uv` will automatically use or install a compatible Python.)


### Setup
1) Clone the repo:
```bash
git clone https://github.com/isacsahlberg/grabAreena.git
cd grabAreena
```
2) Install the command-line tool using uv:
```bash
uv tool install .
```
`uv` builds the package, resolves and installs dependencies (e.g., `requests`, `termcolor`) into an isolated tool environment, and adds a `grabareena` command to your `PATH`.

3) Run
```bash
grabareena --help
```
to verify the installation.
For uninstalling, run
```bash
uv tool uninstall grabareena
```


### Project structure
```bash
grabAreena/
├─ pyproject.toml
├─ README.md
├─ CHANGELOG.md
└─ grabareena/
   ├─ __init__.py
   ├─ cache.py
   ├─ cli.py
   ├─ models.py
   ├─ parse.py
   ├─ print.py
   └─ utils.py
```
There's also the development helpers that are not packaged
```bash
├─ .python-version
├─ run_dev.py       # tiny runner for local dev
└─ uv.lock
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
grabareena [OPTIONS]
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


### Usage examples
```bash
# Default date is today
grabareena                          # find matches for default pattern arguments, today
grabareena -t                       # find matches for default pattern arguments, tomorrow
# The simple flags can be combined
grabareena -a                       # print the entire schedule for today
grabareena -at                      # print the entire schedule for tomorrow
# Pattern flags can be compounded
grabareena -p "Bach, Mozart"        # find matches for specific composers (or any program substrings)
grabareena -p "Bach" -p "Mozart"    # same
```
Combining many just looks like this
```bash
grabareena --date 2025-12-24 --all --pattern "Bach"
```
Attempting to access data for dates more than ±3 days away from today will probably fail, you'll just get something like: `{"developerMessage":"Specified date is beyond current program guide scope"`. One week into the past seems to be working fine.


### Dev usage: You can run the most up-to-date version of the tool in the repo (without reinstalling) using uv
```bash
# run the package module
uv run -m grabareena.cli --help

# alternatively, run the tiny helper
uv run run_dev.py [OPTIONS]

# or equivalently
source .venv/bin/activate
python run_dev.py [OPTIONS]
```
or from anywhere:
```bash
uv run --project ~/path/to/repo ~/path/to/repo/run_dev.py
```
The easiest way is probably to use alias on the full `uv` command:
```bash
alias grabAreena_dev='uv run --project ~/path/to/repo ~/path/to/repo/run_dev.py'
```
After local edits, update the installed CLI using
```bash
uv tool install --force .
```


### Notes / Implementation details
- Titles/descriptions are printed “as is” (punctuation preserved).
- Times that cross midnight are marked with a leading “+” on the following day.
- Cache writes are atomic (tmp+replace). Corrupt/missing cache -> refetch with -r.
- Minimal error handling by design; failures should be obvious and easy to fix.
- The source data can have typos (yes, really), so don't judge this tool too harshly.


### TODO
- Optional diacritic-insensitive matching (e.g., Dvořák ≈ Dvorak).
