# Changelog
All notable changes to this project will be documented here.



## [Unreleased]
[For new updates, add content here, rename this header to the new version (e.g. `[0.2.1]`), and create a new Unreleased one above.]


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
