# Changelog


## [0.3.1] - 2025-10-31
- Add usage logging; point log file to `~/.grabareena/logs/log.txt`, and also switch the cache path to `~/.grabareena/cache/`.
- Start to add some log.debug() statements, but only in the main `grabareena/cli.py` file.
- Add argument `-v/--verbose` to enable DEBUG mode for the logging. `log.debug(...)` calls are present but silent unless verbose is enabled.


## [0.3.0] - 2025-10-23
Instead of running `./main.py` which just calls `grabareena/cli.py`, this version makes the project a uv-installable command-line tool: `grabareena` → `grabareena.cli:main`, and is installable using
```bash
uv tool install .
```
There is still a `run_dev.py` in the repo root for local development, which doesn't change the tool itself. To update local edits, run
```bash
uv tool install --force .
```


## [0.2.0] - 2025-10-09
### Added
- New CLI (`main.py` / `grabareena/cli.py`). Usual flags (output differs a bit from previous version):
  - `-p/--pattern "Bach,Mozart"` — comma-separated matches (case-insensitive)
  - `-P/--programs` — list programmes (now includes the Areena URL on the same line)
  - `-a/--all` — print all pieces
  - `-d/--date YYYY-MM-DD`, `-t/--tomorrow` — choose the day
  - `-l/--language fi|sv`, `-r/--refresh` — endpoint language, bypass cache
- Local caching under `~/.cache/grabareena/{channel}/{YYYY-MM-DD}.json`.
- Programme URLs extracted from deeplinks (e.g. `yleareena://items/1-…`) → `https://areena.yle.fi/1-…`.
- Clean output with aligned columns; supports midnight rollover (`+HH:MM` for pieces after midnight).

### Changed
- Switched data source from HTML scraping to the Areena web app’s **JSON schedule** endpoint.
- Parsing rewritten: programme descriptions are split into Piece objects, with start–end times similar to before. Similarly for Programme objects, which contain a list of Pieces.
- Environment now pinned via **uv**; dependencies managed in `pyproject.toml`.

### Removed
- Old scraper playground scripts and ad-hoc utilities (now under `obsolete/` or deleted).

### Migration notes
- Run once: `uv sync` (sets up the venv and deps).
- Usage examples:
  - `uv run python main.py -P`
  - `uv run python main.py -p "Bach,Mozart"`
  - `uv run python main.py --tomorrow -P`
- Output formatting changed slightly; programme URLs are printed on the same line.


## [0.1.x] - Legacy (HTML scraper era)
- Early versions that parsed Yle’s HTML programme pages directly.
